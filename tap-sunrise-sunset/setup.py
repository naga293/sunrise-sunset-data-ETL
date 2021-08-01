#!/usr/bin/env python
from setuptools import setup

setup(
    name="tap-sunrise-sunset",
    version="0.1.0",
    description="Singer.io tap for extracting data",
    author="Stitch",
    url="http://singer.io",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["tap_sunrise_sunset"],
    install_requires=[
        # NB: Pin these to a more specific version for tap reliability
        "singer-python",
        "requests",
    ],
    entry_points="""
    [console_scripts]
    tap-sunrise-sunset=tap_sunrise_sunset:main
    """,
    packages=["tap_sunrise_sunset"],
    package_data = {
        "schemas": ["tap_sunrise_sunset/schemas/*.json"]
    },
    include_package_data=True,
)
