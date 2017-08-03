# Kiwi Fork

This fork allows specifying packages to be removed from the static typechecking.

Each package can have its own section in a mypy config file, and there you can add an option for skipping the check there.

The following example will skip all checks in `kw.booking.schemas`
mypy.ini

    [mypy-kw.booking.schemas.*]
    skip = True
