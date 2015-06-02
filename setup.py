#!/usr/bin/env python

from vstruct import __version__
from setuptools import setup


description = "vivisect vstruct."
setup(name="vivisect-vstruct",
      version=__version__,
      description=description,
      long_description=description,
      license="Apache 2.0 License",
      packages=["vstruct"])
