import setuptools
import os

with open("README.rst", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="minimal_bibtex_io_sebastian-achim-mueller",
    version="0.0.3",
    author="Sebastian Achim Mueller",
    author_email="sebastian-achim.mueller@mpi-hd.mpg.de",
    description="A minimal loader and dumper for bibtex-files",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/relleums/minimal_bibtex_io",
    project_urls={
        "Bug Tracker": "https://github.com/relleums/minimal_bibtex_io/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Markup :: LaTeX",
    ],
    packages=["minimal_bibtex_io",],
    package_data={
        "minimal_bibtex_io": [
            os.path.join("tests", "resources", "example.bib")
        ],
    },
    python_requires=">=3.0",
)
