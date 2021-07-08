import minimal_bibtex_io as mbib
import pkg_resources
import os
import pytest
import tempfile

example_bib_path = pkg_resources.resource_filename(
    "minimal_bibtex_io", os.path.join("tests", "resources", "example.bib")
)


MIN_BIB = b"@type{citekey,a={A},b={B}}"

MIN_LINEBREAKS_BIB = b"@type\r\n{citekey\n\r,a={A\r},b=\n{B}}"

MIN_WHITESPACE_BIB = b"@type  { \n\r citekey\n  ,  a  = {A\r},b=\n{B} }"


def MIN_is_valid(rawbib):
    assert len(rawbib["entries"]) == 1
    rawentry = rawbib["entries"][0]
    assert rawentry["type"] == b"type"
    assert rawentry["citekey"] == b"citekey"
    assert rawentry["fields"][b"a"] == b"A"
    assert rawentry["fields"][b"b"] == b"B"


def test_minimal():
    rawbib = mbib.loads(MIN_BIB)
    MIN_is_valid(rawbib)


def test_linebreaks():
    rawbib = mbib.loads(MIN_LINEBREAKS_BIB)
    MIN_is_valid(rawbib)


def test_whitespaces():
    rawbib = mbib.loads(MIN_WHITESPACE_BIB)
    MIN_is_valid(rawbib)


def test_example_bib():
    with open(example_bib_path, "rb") as f:
        rawbib = mbib.loads(f.read())

    assert len(rawbib["preambles"]) == 3
    assert rawbib["preambles"][0] == b'"\\makeatletter"'
    assert (
        rawbib["preambles"][1]
        == b'"\\@ifundefined{url}{\\def\\url#1{\\texttt{#1}}}{}"'
    )
    assert rawbib["preambles"][2] == b'"\\makeatother"'

    assert len(rawbib["strings"]) == 1
    rawbib["strings"][0]["fields"][b"AW"] == b"Addison-Wesley"

    assert len(rawbib["entries"]) == 4

    companion = rawbib["entries"][0]
    assert companion["type"] == b"book"
    assert companion["citekey"] == b"companion"
    assert (
        companion["fields"][b"author"]
        == b"Goossens, Michel and Mittelbach, Franck and Samarin, Alexander"
    )
    assert isinstance(companion["fields"][b"year"], int)
    assert companion["fields"][b"year"] == 1993

    tricky = rawbib["entries"][2]
    assert tricky["type"] == b"pitfall"
    assert tricky["citekey"] == b"tricky"
    tricky["fields"][b"titleone"] == b'Comments on {"}Filenames and Fonts{"}'
    tricky["fields"][b"titletwo"] == b'Comments on "Filenames and Fonts"'


def test_dump_and_load():
    with open(example_bib_path, "rb") as f:
        rawbib = mbib.loads(f.read())

    A = mbib.normalize(rawbib)

    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "out.bib"), "wt") as f:
            f.write(mbib.dumps(A))
        with open(os.path.join(tmpdir, "out.bib"), "rb") as f:
            rawbib_back = mbib.loads(f.read())
            B = mbib.normalize(rawbib_back)

    assert len(A["entries"]) == len(B["entries"])
    for i in range(len(A["entries"])):
        eA = A["entries"][i]
        eB = B["entries"][i]
        assert eA["type"] == eB["type"]
        assert eA["citekey"] == eB["citekey"]
        assert len(eA["fields"]) == len(eB["fields"])
        for fkey in eA["fields"]:
            assert fkey in eB["fields"]
            assert eA["fields"][fkey] == eB["fields"][fkey]

    assert len(A["strings"]) == len(B["strings"])
    for i in range(len(A["strings"])):
        sA = A["strings"][i]
        sB = B["strings"][i]
        assert len(sA["fields"]) == len(sB["fields"])
        for fkey in sA["fields"]:
            assert fkey in sB["fields"]
            assert sA["fields"][fkey] == sB["fields"][fkey]

    assert len(A["preambles"]) == len(B["preambles"])
    for i in range(len(A["preambles"])):
        A["preambles"][i] == B["preambles"][i]


def test_stripper():
    assert b"W" == mbib._strip_latex(b" W")
    assert b"W" == mbib._strip_latex(b"W ")
    assert b"W" == mbib._strip_latex(b" W ")
    assert b"1 2" == mbib._strip_latex(b" 1 2 ")
    assert b"1 2" == mbib._strip_latex(b"1  2")
    assert b"1 2" == mbib._strip_latex(b" 1  2")
    assert b"1 2" == mbib._strip_latex(b" 1  2 ")
    assert b"1 2" == mbib._strip_latex(b" 1\n\n2")
    assert b"" == mbib._strip_latex(b"")


def test_advance():
    assert b"" == mbib._advance(b"", -1)
    assert b"abcdefg" == mbib._advance(b"abcdefg", -1)
    assert b" bcdefg" == mbib._advance(b"abcdefg", 0)
    assert b"       " == mbib._advance(b"abcdefg", 6)
    with pytest.raises(AssertionError) as exc_info:
        mbib._advance(b"abcdefg", 7)
    with pytest.raises(AssertionError) as exc_info:
        mbib._advance(b"abcdefg", -2)


def test_find_braces():
    #                                     01234567
    b, e = mbib._find_braces_start_stop(b"{abcdef}")
    assert b == 0
    assert e == 7

    b, e = mbib._find_braces_start_stop(b"{a{de}f}")
    assert b == 0
    assert e == 7

    b, e = mbib._find_braces_start_stop(b"{a}de{f}")
    assert b == 0
    assert e == 2

    #                                     0         1
    #                                     01234567890123
    b, e = mbib._find_braces_start_stop(b"abc {a} de {f}")
    assert b == 4
    assert e == 6

    b, e = mbib._find_braces_start_stop(b"abc")
    assert b == -1
    assert e == -1

    b, e = mbib._find_braces_start_stop(b"")
    assert b == -1
    assert e == -1



def test_find_first_non_space():
    assert mbib._find_first_non_space(b"") == -1
    assert mbib._find_first_non_space(b"hand") == 0
    assert mbib._find_first_non_space(b" hans") == 1
    assert mbib._find_first_non_space(b" hans ") == 1
    assert mbib._find_first_non_space(b" \nhans ") == 2
    assert mbib._find_first_non_space(b" \thans ") == 2
    assert mbib._find_first_non_space(b"\n\n\n\thans ") == 4


def test_find_first_non_digit():
    assert mbib._find_first_non_digit(b"") == -1
    assert mbib._find_first_non_digit(b"123abc") == 3
    assert mbib._find_first_non_digit(b"   abc") == 0
    assert mbib._find_first_non_digit(b"1  abc") == 1


def test_brace_balance():
    assert mbib._brace_balance(b"") == []
    assert mbib._brace_balance(b"{}") == [1,0]
    assert mbib._brace_balance(b"}{") == [-1,0]
    assert mbib._brace_balance(b"{{}}") == [1,2,1,0]
    assert mbib._brace_balance(b"oo{aa{bb}cc}dd") == [
        0,0,1,1,1,2,2,2,1,1,1,0,0,0
    ]


def test_find_first_quote_not_escaped():
    assert mbib._find_first_quote_not_escaped(b'') == -1
    assert mbib._find_first_quote_not_escaped(b' ') == -1
    assert mbib._find_first_quote_not_escaped(b'"') == 0
    assert mbib._find_first_quote_not_escaped(b'\\"') == -1
    assert mbib._find_first_quote_not_escaped(b'{"}') == -1
    assert mbib._find_first_quote_not_escaped(b'{"}"') == 3
    assert mbib._find_first_quote_not_escaped(b'abc{"la"la"} hui') == -1
    assert mbib._find_first_quote_not_escaped(b'abc{"la"la"} hui"') == 16
