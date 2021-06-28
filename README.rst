Minimal parser for bibliography .bib-files 
==========================================
|BlackStyle|

Follows the format described by Nicolas Markey in "Tame the BeaST" from October 2009.
All this does is reading bib-bytes and structuring the keys and fields in a dictionary.

Usage
-----
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
