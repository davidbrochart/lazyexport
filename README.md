# lazyexport

Extracted from [AnyIO](https://github.com/agronholm/anyio)'s lazy importer.

## Usage

```python
from typing import TYPE_CHECKING
from lazyexport import install, fix_package_names

if TYPE_CHECKING or not install():
    # Declare your public exports here
    from ._client import Client as Client

    fix_package_names()  # optional
```

Place this in the module that exposes your public exports.
Public exports are loaded when first accessed. Lazy loading requires access to
the exporting module's Python source to discover its imports. If the source
cannot be inspected, for example in an installation containing only compiled
`.pyc` files, imports run normally instead.

Lazy loading sets exported objects' `__module__` to the exporting module's name,
so a class exposed by `mypackage` appears to belong to `mypackage` rather than
`mypackage._client`. The optional `fix_package_names()` call applies similar
rewriting when imports run eagerly, removing private components from module names.
This affects introspection, documentation, and pickling; imports work without it.

The following import forms are supported:

```python
if TYPE_CHECKING or not install():
    from another_package import Client  # absolute import
    from ._server import Server  # relative import
    from ._client import Client as PublicClient  # export alias
    from . import submodule  # lazy submodule access
```

The following declarations are unsupported:

```python
if TYPE_CHECKING or not install():
    from ._client import *  # raises an error
    import another_package  # not collected as a lazy export

    if some_condition:
        from ._server import Server  # nested imports are not collected
```

Map deprecated names to their replacements with `set_deprecated_aliases()`:

```python
from typing import TYPE_CHECKING
from lazyexport import install, set_deprecated_aliases

if TYPE_CHECKING or not install():
    from ._client import Client as Client

    set_deprecated_aliases({"OldClient": "mypackage.Client"})
```

Accessing `mypackage.OldClient` returns `mypackage.Client` and emits a
`DeprecationWarning`.

## Development

```sh
uv sync --group dev
uv run pytest
```

## Releasing

Add a fragment in `changelog.d/` for each user-facing change; see
[changelog.d/README.rst](changelog.d/README.rst) for naming and types.

Set `project.version` in `pyproject.toml` to the release version, then preview
and generate the changelog (using that same version):

```sh
uv run --group dev towncrier build --draft --version 0.1.0
uv run --group dev towncrier build --yes --version 0.1.0
```

Commit the version update, generated `CHANGELOG.rst`, and deleted fragments.
Push the commit, then push a matching version tag:

```sh
git tag 0.1.0
git push origin 0.1.0
```
