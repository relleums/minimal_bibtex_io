Minimal bibtex io
=================
|BlackStyle|

Format according to "Tame the BeaST" by Nicolas Markey, Oct. 2009.

- ``@TYPE{citekey, key = {value}, ...}``, This will be loaded as
  bib-entry of type ``TYPE``

- ``@string{key = {value}, ...}``

- ``@preamble{value}``

Functions
---------

``loads``
~~~~~~~~~
Loads the raw bytes of a bibtex-file into a dictionary and makes only minimal assumptions on the structrue but not on the content.

``normalize``
~~~~~~~~~~~~~
Takes the raw bib-dictionary and tries to decode and normalize it.
All optionally. It strips away leading, trailing, and consecutive whitespaces.
It converts all keys, entrytypes, and citekyes to lowercase.
It decodes keys and/or values to ''ascii''.

``dumps``
~~~~~~~~~
Dumps a normalized (all ``ascii`` string) bib-dictionary into a bib-file-string.

Example
-------
.. code:: python

    import minimal_bibtex_io as mbib

    # Read bytes, make no assumptions on keys or encoding
    with open("minimal_bibtex_io/tests/resources/example.bib", "rb") as f:
        rawbib = mbib.loads(f.read())

    # Try to decode to ascii and set keys to lower case
    bib = mbib.normalize(rawbib)

    entry = {"type": "book", "citekey": "kasperle1887", "fields": {}}
    entry["fields"]["title"] = "The hills are green"
    entry["fields"]["year"] = 1887
    entry["fields"]["whateverkeyiwant"] = "This is only relevant for me."
    bib["entries"].append(entry)

    # eventually ...
    with open("my.bib", "wt") as f:
        f.write(mbib.dumps(bib, indent=4, width=79))

.. |BlackStyle| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
