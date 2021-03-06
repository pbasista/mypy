MYPY = False
if MYPY:
    from typing_extensions import Final

PYTHON2_VERSION = (2, 7)  # type: Final
PYTHON3_VERSION = (3, 6)  # type: Final
PYTHON3_VERSION_MIN = (3, 4)  # type: Final
CACHE_DIR = '.mypy_cache'  # type: Final
CONFIG_FILE = 'mypy.ini'  # type: Final
SHARED_CONFIG_FILES = ('setup.cfg',)  # type: Final
USER_CONFIG_FILES = ('~/.mypy.ini',)  # type: Final
CONFIG_FILES = (CONFIG_FILE,) + SHARED_CONFIG_FILES + USER_CONFIG_FILES  # type: Final

# This must include all reporters defined in mypy.report. This is defined here
# to make reporter names available without importing mypy.report -- this speeds
# up startup.
REPORTER_NAMES = ['linecount',
                  'any-exprs',
                  'linecoverage',
                  'memory-xml',
                  'cobertura-xml',
                  'xml',
                  'xslt-html',
                  'xslt-txt',
                  'html',
                  'txt']  # type: Final
