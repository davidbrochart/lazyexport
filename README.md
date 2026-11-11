# lazyexport

Lazy package exports from ordinary import declarations. Extracted from AnyIO's
lazy importer, under its MIT license. Requires Python 3.11 or later and has no
runtime dependencies.

```python
from typing import TYPE_CHECKING
from lazyexport import install, fix_package_names

if TYPE_CHECKING or not install():
    from ._client import Client as Client

    fix_package_names()
```

Place this in your package's `__init__.py` (ordinary modules also work).
`install()` reads the calling module's source and builds a map of exports from
the imports in the conditional block. It installs module-level `__getattr__`
and `__dir__` hooks and returns True, skipping the eager imports. Accessing an
export imports its implementation and caches the value in the calling module.
If source is unavailable, it returns False and the imports execute eagerly.
`fix_package_names()` makes implementation module names public in that fallback.
The lazy path also rewrites exported objects' `__module__` to the exporting module.

## Supported declarations

Use direct `from module import name` statements inside the top-level
`if TYPE_CHECKING or not install():` block. Relative imports and export aliases
are supported. `from . import submodule` exposes submodules lazily. Star imports,
plain `import module` declarations, and nested import declarations are unsupported.
Use the unaliased helper names shown here.

For deprecated names, import `set_deprecated_aliases` from lazyexport and call it
inside the block with a literal dictionary mapping old names to fully qualified
replacement names. Access emits DeprecationWarning. Lazy resolutions are cached;
the eager fallback warns on each access.

The installer replaces existing `__getattr__` and `__dir__` hooks. `dir()` lists
mapped attribute exports. Define `__all__` explicitly if you need star exports;
star importing resolves those exports eagerly. References to missing names inside
the exporting module do not trigger `__getattr__`; use this for exports consumed
through module attribute access or `from` imports.

## Development

```sh
python -m pip install -e '.[test]'
python -m pytest
```

## Releasing

Set `project.version` in `pyproject.toml` to the release version and commit it,
including `.github/workflows/release.yml`. Push the commit, then push a matching
version tag:

```sh
git tag 0.1.0
git push origin 0.1.0
```

The release workflow tests the package, builds and checks the wheel and source
distribution, and publishes them to PyPI using trusted publishing. The tag must
match the package version exactly (no `v` prefix). Configure the PyPI trusted
publisher with this repository and workflow filename `release.yml`, leaving the
environment field empty. No API token is required.
