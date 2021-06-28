import setuptools
import os

with open("README.rst", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="minimal_bibtex_io",
    version="0.0.0",
    description="A minimal restrictive parser and writer for bibliography bib-files",
    long_description=long_description,
    url="https://github.com/relleums",
    author="Sebastian Achim Mueller",
    author_email="sebastian-achim.mueller@mpi-hd.mpg.de",
    license="MIT",
    packages=["minimal_bibtex_io",],
    package_data={
        "minimal_bibtex_io": os.path.join("tests", "resources", "*")
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Intended Audience :: Science/Research",
    ],
)
