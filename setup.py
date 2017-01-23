#!/usr/bin/env python

import glob
import os
import os.path
import sys

if sys.version_info < (3, 2, 0):
    sys.stderr.write("ERROR: You need Python 3.2 or later to use mypy.\n")
    exit(1)

# This requires setuptools when building; setuptools is not needed
# when installing from a wheel file (though it is still neeeded for
# alternative forms of installing, as suggested by README.md).
from setuptools import setup
from setuptools.command.build_py import build_py
from mypy.version import base_version
from mypy import git

git.verify_git_integrity_or_abort(".")

version = base_version
description = 'Optional static typing for Python'
long_description = '''
Mypy -- Optional Static Typing for Python
=========================================

Add type annotations to your Python programs, and use mypy to type
check them.  Mypy is essentially a Python linter on steroids, and it
can catch many programming errors by analyzing your program, without
actually having to run it.  Mypy has a powerful type system with
features such as type inference, gradual typing, generics and union
types.
'''.lstrip()


def find_package_data_files(package_name, base, globs):
    """Find all interesting package data files, for setup(package_data=)

    Arguments:
      package_name: The package name.
      base:  The directory to search in.
      globs: A list of glob patterns to accept files.
    """

    rv_dirs = [root for root, dirs, files in os.walk(os.path.join(package_name, base))]
    rv = []
    for rv_dir in rv_dirs:
        files = []
        for pat in globs:
            files += glob.glob(os.path.join(rv_dir, pat))
        if not files:
            continue
        rv.extend([os.path.relpath(x, package_name) for x in files])

    return rv


class CustomPythonBuild(build_py):
    def pin_version(self):
        path = os.path.join(self.build_lib, 'mypy')
        self.mkpath(path)
        with open(os.path.join(path, 'version.py'), 'w') as stream:
            stream.write('__version__ = "{}"\n'.format(version))

    def run(self):
        self.execute(self.pin_version, ())
        build_py.run(self)


mypy_res_files = []

mypy_res_files += find_package_data_files('mypy_res', 'typeshed', ['*.py', '*.pyi'])

mypy_res_files += find_package_data_files('mypy_res', 'xml', ['*.xsd', '*.xslt', '*.css'])

classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Software Development',
]


scripts = ['scripts/stubgen']

# These requirements are used when installing by other means than bdist_wheel.
# E.g. "pip3 install ." or
# "pip3 install git+git://github.com/python/mypy.git"
# (as suggested by README.md).
install_requires = []
install_requires.append('typed-ast >= 0.6.3')
if sys.version_info < (3, 5):
    install_requires.append('typing >= 3.5.3')

setup(name='mypy',
      version=version,
      description=description,
      long_description=long_description,
      author='Jukka Lehtosalo',
      author_email='jukka.lehtosalo@iki.fi',
      url='http://www.mypy-lang.org/',
      license='MIT License',
      platforms=['POSIX'],
      py_modules=[],
      packages=['mypy', 'mypy_res'],
      package_data={
          'mypy_res': mypy_res_files,
      },
      scripts=scripts,
      classifiers=classifiers,
      cmdclass={'build_py': CustomPythonBuild},
      install_requires=install_requires,
      entry_points={
          'console_scripts': [
              'mypy=mypy.main:main',
          ],
      },
      )
