import re
import sys
import os

from typing import Optional, Tuple, Sequence, MutableSequence, List, MutableMapping, IO
from types import ModuleType


# Type Alias for Signatures
Sig = Tuple[str, str]


def parse_signature(sig: str) -> Optional[Tuple[str,
                                                List[str],
                                                List[str]]]:
    m = re.match(r'([.a-zA-Z0-9_]+)\(([^)]*)\)', sig)
    if not m:
        return None
    name = m.group(1)
    name = name.split('.')[-1]
    arg_string = m.group(2)
    if not arg_string.strip():
        return (name, [], [])
    args = [arg.strip() for arg in arg_string.split(',')]
    fixed = []
    optional = []
    i = 0
    while i < len(args):
        if args[i].startswith('[') or '=' in args[i]:
            break
        fixed.append(args[i].rstrip('['))
        i += 1
        if args[i - 1].endswith('['):
            break
    while i < len(args):
        arg = args[i]
        arg = arg.strip('[]')
        arg = arg.split('=')[0]
        optional.append(arg)
        i += 1
    return (name, fixed, optional)


def build_signature(fixed: Sequence[str],
                    optional: Sequence[str]) -> str:
    args = []  # type: MutableSequence[str]
    args.extend(fixed)
    for arg in optional:
        if arg.startswith('*'):
            args.append(arg)
        else:
            args.append('%s=...' % arg)
    sig = '(%s)' % ', '.join(args)
    # Ad-hoc fixes.
    sig = sig.replace('(self)', '')
    return sig


def parse_all_signatures(lines: Sequence[str]) -> Tuple[List[Sig],
                                                        List[Sig]]:
    sigs = []
    class_sigs = []
    for line in lines:
        line = line.strip()
        m = re.match(r'\.\. *(function|method|class) *:: *[a-zA-Z_]', line)
        if m:
            sig = line.split('::')[1].strip()
            parsed = parse_signature(sig)
            if parsed:
                name, fixed, optional = parsed
                if m.group(1) != 'class':
                    sigs.append((name, build_signature(fixed, optional)))
                else:
                    class_sigs.append((name, build_signature(fixed, optional)))

    return sorted(sigs), sorted(class_sigs)


def find_unique_signatures(sigs: Sequence[Sig]) -> List[Sig]:
    sig_map = {}  # type: MutableMapping[str, List[str]]
    for name, sig in sigs:
        sig_map.setdefault(name, []).append(sig)
    result = []
    for name, name_sigs in sig_map.items():
        if len(set(name_sigs)) == 1:
            result.append((name, name_sigs[0]))
    return sorted(result)


def is_c_module(module: ModuleType) -> bool:
    return ('__file__' not in module.__dict__ or
            os.path.splitext(module.__dict__['__file__'])[-1] in ['.so', '.pyd'])


def write_header(file: IO[str], module_name: Optional[str] = None,
                 pyversion: Tuple[int, int] = (3, 5)) -> None:
    if module_name:
        if pyversion[0] >= 3:
            version = '%d.%d' % (sys.version_info.major,
                                 sys.version_info.minor)
        else:
            version = '2'
        file.write('# Stubs for %s (Python %s)\n' % (module_name, version))
    file.write(
        '#\n'
        '# NOTE: This dynamically typed stub was automatically generated by stubgen.\n\n')


def infer_sig_from_docstring(docstr: str, name: str) -> Optional[Tuple[str, str]]:
    if not docstr:
        return None
    docstr = docstr.lstrip()
    # look for function signature, which is any string of the format
    # <function_name>(<signature>) -> <return type>
    # or perhaps without the return type

    # in the signature, we allow the following characters:
    # colon/equal: to match default values, like "a: int=1"
    # comma/space/brackets: for type hints like "a: Tuple[int, float]"
    # dot: for classes annotating using full path, like "a: foo.bar.baz"
    # to capture return type,
    sig_str = r'\([a-zA-Z0-9_=:, \[\]\.]*\)'
    sig_match = r'%s(%s)' % (name, sig_str)
    # first, try to capture return type; we just match until end of line
    m = re.match(sig_match + ' -> ([a-zA-Z].*)$', docstr, re.MULTILINE)
    if m:
        # strip potential white spaces at the right of return type
        return m.group(1), m.group(2).rstrip()

    # try to not match return type
    m = re.match(sig_match, docstr)
    if m:
        return m.group(1), 'Any'
    return None


def infer_prop_type_from_docstring(docstr: str) -> Optional[str]:
    if not docstr:
        return None

    # check for Google/Numpy style docstring type annotation
    # the docstring has the format "<type>: <descriptions>"
    # in the type string, we allow the following characters
    # dot: because something classes are annotated using full path,
    # brackets: to allow type hints like List[int]
    # comma/space: things like Tuple[int, int]
    test_str = r'^([a-zA-Z0-9_, \.\[\]]*): '
    m = re.match(test_str, docstr)
    return m.group(1) if m else None
