import tempfile
import shutil
from pathlib import Path


import pytest
from fsspec.implementations.local import LocalFileSystem
from fsspec.registry import (
    register_implementation,
    _registry
)


class DummyTestFS(LocalFileSystem):
    protocol = "mock"


@pytest.fixture(scope='session')
def clear_registry():
    register_implementation("mock", DummyTestFS)
    try:
        yield
    finally:
        _registry.clear()


@pytest.fixture()
def testingdir(clear_registry):
    tempdir = tempfile.TemporaryDirectory()
    tempdir = tempdir.name
    tmp = Path(tempdir)
    tmp.mkdir()
    folder1 = tmp.joinpath('folder1')
    folder1.mkdir()
    folder1_files = ['file1.txt', 'file2.txt']
    for f in folder1_files:
        p = folder1.joinpath(f)
        p.touch()
        p.write_text(f)

    file1 = tmp.joinpath('file1.txt')
    file1.touch()
    file1.write_text('hello world')
    file2 = tmp.joinpath('file2.txt')
    file2.touch()
    file2.write_bytes(b'hello world')
    yield tempdir
    shutil.rmtree(tempdir)

@pytest.fixture()
def hdfs_test_client():
    import os
    pyarrow = pytest.importorskip('pyarrow')
    host = os.environ.get('ARROW_HDFS_TEST_HOST', '0.0.0.0')
    user = os.environ.get('ARROW_HDFS_TEST_USER', 'hdfs')
    try:
        port = int(os.environ.get('ARROW_HDFS_TEST_PORT', 9000))
    except ValueError:
        raise ValueError('Env variable ARROW_HDFS_TEST_PORT was not '
                         'an integer')

    hdfs = pyarrow.hdfs.connect(host='0.0.0.0', port=9000, user=user, driver='libhdfs3')
    hdfs.mkdir('/folder1')
    return host, user, port

