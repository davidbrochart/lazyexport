from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

from lazyexport import _build_lazy_map
from types import ModuleType


@pytest.fixture
def package(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.syspath_prepend(str(tmp_path))
    root = tmp_path / 'example_export'
    root.mkdir()
    (root / '_impl.py').write_text('class Client: pass\n')
    yield root
    for name in list(sys.modules):
        if name == 'example_export' or name.startswith('example_export.'):
            del sys.modules[name]


def test_lazy_export(package: Path) -> None:
    (package / '__init__.py').write_text('''from typing import TYPE_CHECKING
from lazyexport import install, fix_package_names, set_deprecated_aliases
if TYPE_CHECKING or not install():
    from ._impl import Client as PublicClient
    fix_package_names()
    set_deprecated_aliases({'OldClient': 'example_export.PublicClient'})
''')
    module = importlib.import_module('example_export')
    assert 'example_export._impl' not in sys.modules
    assert 'PublicClient' in dir(module)
    client = module.PublicClient
    assert client is module.PublicClient
    assert module.__dict__['PublicClient'] is client
    assert client.__module__ == 'example_export'
    with pytest.warns(DeprecationWarning):
        assert module.OldClient is client
    with pytest.raises(AttributeError):
        module.missing


def test_submodule_only(package: Path) -> None:
    (package / '__init__.py').write_text('''from typing import TYPE_CHECKING
from lazyexport import install
if TYPE_CHECKING or not install():
    from . import _impl
''')
    module = importlib.import_module('example_export')
    assert 'example_export._impl' not in sys.modules
    assert module._impl.__name__ == 'example_export._impl'


def test_eager_fallback(package: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import lazyexport

    def unavailable(module: ModuleType) -> str:
        raise OSError('source unavailable')

    monkeypatch.setattr(lazyexport.inspect, 'getsource', unavailable)
    (package / '__init__.py').write_text('''from typing import TYPE_CHECKING
from lazyexport import install, fix_package_names, set_deprecated_aliases
if TYPE_CHECKING or not install():
    from ._impl import Client as Client
    fix_package_names()
    set_deprecated_aliases({'OldClient': 'example_export.Client'})
''')
    module = importlib.import_module('example_export')
    assert 'example_export._impl' in sys.modules
    assert module.Client.__module__ == 'example_export'
    with pytest.warns(DeprecationWarning):
        assert module.OldClient is module.Client


def test_fileless_module() -> None:
    assert _build_lazy_map(ModuleType('fileless')) == ({}, {}, [])
