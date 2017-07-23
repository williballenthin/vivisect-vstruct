#!/usr/bin/env python

import setuptools


description = "Unofficial packaged vivisect vstruct mirror."
setuptools.setup(name="vivisect-vstruct-wb",
      version="1.0.3",
      description=description,
      long_description=description,
      url="https://github.com/williballenthin/vivisect-vstruct",
      author="invisig0th, mirrored by Willi Ballenthin",
      author_email="willi.ballenthin@gmail.com",
      packages=setuptools.find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
      classifiers=[
          "Intended Audience :: Developers",
          'Programming Language :: Python :: 2.7',
      ])
