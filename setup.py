"""Setup script for ecto easy installation"""

try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

import os
import sys
import platform

from distutils import log
from distutils.command.build_ext import build_ext as _build_ext

from setuptools import setup, Extension

CONTAINING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
try:
    from utils import copydir, get_version_from_tag
    __version__ = get_version_from_tag()
    open(os.path.join(CONTAINING_DIRECTORY,"qibuild_ws/ecto/python/VERSION"), "w").write(__version__)
except ImportError:
    __version__=open(os.path.join(CONTAINING_DIRECTORY,"qibuild_ws/ecto/python/VERSION")).read().split()[0]

# make sure that setup.py is run with an allowed python version
def check_allowed_python_version():
    import re
    pattern = "'Programming Language :: Python :: (\d+)\.(\d+)'"
    supported = []
    with open(__file__) as setup:
        for line in setup.readlines():
            found = re.search(pattern, line)
            if found:
                major = int(found.group(1))
                minor = int(found.group(2))
                supported.append( (major, minor) )
    this_py = sys.version_info[:2]
    if this_py not in supported:
        print("only these python versions are supported:", supported)
        sys.exit(1)

check_allowed_python_version()

# Change the cwd to our source dir
try:
    this_file = __file__
except NameError:
    this_file = sys.argv[0]
this_file = os.path.abspath(this_file)
if os.path.dirname(this_file):
    os.chdir(os.path.dirname(this_file))

class ecto_build_ext(_build_ext):

    def __init__(self, *args, **kwargs):
        _build_ext.__init__(self, *args, **kwargs)

    def initialize_options(self):
        _build_ext.initialize_options(self)

    def run(self):
        platform_arch = platform.architecture()[0]
        log.info("Python architecture is %s" % platform_arch)
        self.install_dir = os.path.join(os.getcwd(), "install")
        self.prepare_package()
        for ext in self.extensions:
            self.install_extension(ext)

    def prepare_package(self):
        # Move compiled libraries in lib folder
        if not os.path.exists(os.path.join(self.build_lib, "ecto", "lib")):
            os.makedirs(os.path.join(self.build_lib, "ecto", "lib"))

        copydir(
            os.path.join(
                self.install_dir,
                "lib",
            ),
            os.path.join(
                self.build_lib,
                "ecto",
                "lib"
            ),
            filter=[
                "lib*.so*",
            ],
            recursive=False,
        )

    def install_extension(self, extension):
        ext_subpath_parts = extension.name.split('.')

        ext_path = self.build_lib
        for part in ext_subpath_parts:
            ext_path = os.path.join(ext_path, part)
            if not os.path.exists(ext_path):
                os.mkdir(ext_path)

            ext_init_path = os.path.join(ext_path, "__init__.py")
            if not os.path.exists(ext_init_path):
                with open(ext_init_path, "w") as f:
                    pass

        copydir(
            os.path.join(
                self.install_dir,
                "lib",
                "python2.7",
                "dist-packages",
                *ext_subpath_parts
            ),
            os.path.join(
                ext_path
            ),
            filter=[
                "*.so*",
            ],
            recursive=False,
        )


setup(
    name = "python-ecto",
    version = __version__,
    description = ("Python installer for ecto"),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: C++',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
    ],
    keywords = 'ecto',
    author = 'Surya AMBROSE <surya.ambrose@gmail.com>',
    author_email = 'surya.ambrose@gmail.com',
    packages = [
        'ecto',
        'ecto.impl'
    ],
    package_dir = {
        'ecto': 'qibuild_ws/ecto/python/ecto',
    },
    package_data={"ecto":["VERSION"]},
    cmdclass = {
        'build_ext': ecto_build_ext,
    },

    ext_modules = [
        Extension('ecto', []),
    ],
    eager_resources=["ecto/lib"],
)
