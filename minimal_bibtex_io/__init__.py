"""
Minimal restrictive parser for bibliography bib-files.
"""
import textwrap as _textwrap


def loads(b):
    """
    Returns a raw-byte-bib-dictionary, i.e. keys and values are the raw-bytes
    from the bib-file. Only minimal assumptions on structure are made.
    Expected format is according to:

        Tame the BeaST
        by Nicolas Markey
        markey@lsv.ens-cachan.fr
        Version 1.4
        October 11, 2009

    Parameters
    ----------
    b : bytes
            The raw bytes of a bib-file.
    """
    raw_entries = _split_raw_entries(bib_B=b)

    entries = []
    for _entry_B in raw_entries:
        try:
            entry_B = bytes(_entry_B)
            entry_B = _remove_trailing_comments_from_entry_bytes(
                entry_B=entry_B
            )
            entry_B = bytes.replace(entry_B, b"\r", b"")
            entry_B = bytes.replace(entry_B, b"\n", b"")
            entries.append(entry_B)
        except Exception as err:
            print("Error in: ", entry_B)
            raise err

    bib = {
        "entries": [],
        "strings": [],
        "preambles": [],
    }

    for entry_B in entries:
        try:
            entrytype_B = _parse_entrytype_bytes(entry_B=entry_B)
            if bytes.lower(entrytype_B) == b"string":
                fields_B = _parse_fields_bytes(entry_B=entry_B)
                field_dict = _parse_fields_into_dict(fields_B=fields_B)
                string = {}
                string["fields"] = field_dict
                bib["strings"].append(string)
            elif bytes.lower(entrytype_B) == b"preamble":
                preamble = _parse_preamble_bytes(entry_B=entry_B)
                bib["preambles"].append(preamble)
            else:
                citekey_B = _parse_citekey_bytes(entry_B=entry_B)
                fields_B = _parse_fields_bytes(entry_B=entry_B)
                field_dict = _parse_fields_into_dict(fields_B=fields_B)
                entry = {}
                entry["fields"] = field_dict
                entry["type"] = entrytype_B
                entry["citekey"] = citekey_B
                bib["entries"].append(entry)
        except Exception as err:
            print("Error in: ", entry_B)
            raise err

    return bib


def normalize(
    raw_byte_bib,
    field_keys_lower=True,
    field_keys_ascii=True,
    field_values_ascii=True,
    type_lower=True,
    type_ascii=True,
    citekey_lower=True,
    citekey_ascii=True,
    preamble_values_ascii=True,
):
    """
    Returns a bib-dictionary

    - Converts keys to lower-case
    - Decodes keys to ascii
    - DEcodes values to ascii

    Parameters
    ----------
    field_keys_lower : Bool (True)
            The entrie's field-keys are converted to lower case.
            All field options apply to '@entries' and '@string-entries'.
    field_keys_ascii : Bool (True)
            The entrie's field-keys are decoded in ascii.
    field_values_ascii : Bool (True)
            The entrie's field-values are decoded in ascii.
    type_lower : Bool (True)
            The entrie's type-key is converted to lower case.
    type_ascii : Bool (True)
            The entrie's type-key is decoded in ascii.
    citekey_lower : Bool (True),
            The entrie's cite-key is converted to lower case.
    citekey_ascii : Bool (True)
            The entrie's cite-key is decoded in ascii.
    preamble_values_ascii : Bool (True)
            The preamble-entrie's values are decoded in ascii.
    """
    out = {}
    out["entries"] = []
    for entry in raw_byte_bib["entries"]:
        out["entries"].append(
            _normalize_entry(
                entry=entry,
                field_keys_lower=field_keys_lower,
                field_keys_ascii=field_keys_ascii,
                field_values_ascii=field_values_ascii,
                type_lower=type_lower,
                type_ascii=type_ascii,
                citekey_lower=citekey_lower,
                citekey_ascii=citekey_ascii,
            )
        )

    out["strings"] = []
    for string_entry in raw_byte_bib["strings"]:
        out["strings"].append(
            _normalize_entry(
                entry=string_entry,
                field_keys_lower=field_keys_lower,
                field_keys_ascii=field_keys_ascii,
                field_values_ascii=field_values_ascii,
                type_lower=type_lower,
                type_ascii=type_ascii,
            )
        )

    out["preambles"] = []
    for preamble_entry in raw_byte_bib["preambles"]:
        if preamble_values_ascii:
            out["preambles"].append(_decode_ascii(B=preamble_entry))
        else:
            out["preambles"].append(preamble_entry)
    return out


def dumps(bib, indent=4, width=79):
    """
    Returns a string as in a bib-file from the bibliography.

    Parameters
    ----------
    indent int : 4
            Number of indention-white-spaces before fields in entreis.
    width int : 79
            Max number of columns before wrapping of fields in entries.
    """
    buff = str()
    for preamble in bib["preambles"]:
        buff += "@preamble{"
        buff += preamble
        buff += "}\n"
        buff += "\n"
    for string in bib["strings"]:
        buff += _dumps_entry(
            entrytype="string",
            citekey=None,
            fields=string["fields"],
            indent=indent,
            width=width,
        )
        buff += "\n"
    for entry in bib["entries"]:
        buff += _dumps_entry(
            entrytype=entry["type"],
            citekey=entry["citekey"],
            fields=entry["fields"],
            indent=indent,
            width=width,
        )
        buff += "\n"
    return buff


def _dumps_entry(entrytype, citekey, fields, indent, width):
    buff = str()
    buff += "@" + entrytype + "{"
    if citekey:
        buff += citekey + ","
    buff += "\n"
    buff += _dumps_fields(fields=fields, indent=indent, width=width)
    buff += "}\n"
    return buff


def _dumps_fields(fields, indent, width):
    buff = str()
    for key in fields:
        pre = " " * indent + key + " = "
        if isinstance(fields[key], int):
            value = str(fields[key])
            is_int = True
        else:
            value = "{" + fields[key] + "}"
            is_int = False
        potential_field = pre + value + ","
        if len(potential_field) >= width and not is_int:
            field = pre
            field += "{"
            field += "\n"
            field += " " * 2 * indent
            tmplines = _textwrap.wrap(fields[key], width - 2 * indent)
            field += str.join("\n" + " " * 2 * indent, tmplines)
            field += "\n"
            field += " " * indent + "},"
        else:
            field = potential_field
        field += "\n"
        buff += field
    return buff


def _normalize_entry(
    entry,
    field_keys_lower=True,
    field_keys_ascii=True,
    field_values_strip=True,
    field_values_ascii=True,
    type_lower=True,
    type_ascii=True,
    citekey_lower=True,
    citekey_ascii=True,
):
    out = {}
    if "type" in entry:
        _type = bytes(entry["type"])
        _type = bytes.lower(_type) if type_lower else _type
        _type = _decode_ascii(_type) if type_ascii else _type
        out["type"] = _type

    if "citekey" in entry:
        _ck = bytes(entry["citekey"])
        _ck = bytes.lower(_ck) if citekey_lower else _ck
        _ck = _decode_ascii(_ck) if citekey_ascii else _ck
        out["citekey"] = _ck

    of = {}
    for field_key in entry["fields"]:
        _fk = bytes(field_key)
        _fk = bytes.lower(_fk) if field_keys_lower else _fk
        _fk = _decode_ascii(_fk) if field_keys_ascii else _fk

        if isinstance(entry["fields"][field_key], bytes):
            _val = bytes(entry["fields"][field_key])
            _val = _strip_latex(_val) if field_values_strip else _val
            _val = _decode_ascii(_val) if field_values_ascii else _val
            of[_fk] = _val
        else:
            of[_fk] = entry["fields"][field_key]
    out["fields"] = of
    return out


def _split_into_blocks(B, sep=b"@"):
    _blocks = bytes.split(B, sep=sep)

    blocks = []
    for _block in _blocks:
        if len(_block) > 0:
            block = bytes.join(b"", [sep, _block])
            blocks.append(block)
    return blocks


def _split_raw_entries(bib_B):
    blocks = _split_into_blocks(B=bib_B)

    entries = []
    blkidx = 0
    while blkidx < len(blocks):
        entry = []
        block = blocks[blkidx]
        entry.append(block)
        blkidx += 1
        num_opening = bytes.count(block, b"{")
        num_closing = bytes.count(block, b"}")

        while num_opening != num_closing:
            block = blocks[blkidx]
            entry.append(block)
            blkidx += 1
            num_opening += bytes.count(block, b"{")
            num_closing += bytes.count(block, b"}")

        entries.append(bytes.join(b"", entry))
    return entries


def _remove_trailing_comments_from_entry_bytes(entry_B):
    """
    remove possible comments trailing the '@type{citekey, ...}' entry.
    """
    start, stop = _find_braces_start_stop(B=entry_B)
    return entry_B[0 : stop + 1]


def _parse_entrytype_bytes(entry_B):
    pos_at = bytes.find(entry_B, b"@")
    pos_brace = bytes.find(entry_B, b"{")
    assert pos_at >= 0, "Expected '@' in bib-entry-bytes."
    assert pos_brace >= 0, "Expected '{' in bib-entry-bytes."
    entrykey_B = entry_B[pos_at + 1 : pos_brace]
    entrykey_B = bytes.strip(entrykey_B)
    return entrykey_B


def _parse_citekey_bytes(entry_B):
    pos_brace = bytes.find(entry_B, b"{")
    pos_comma = bytes.find(entry_B, b",")

    assert pos_brace >= 0, "Expected '{' in bib-entry-bytes."
    assert pos_brace < pos_comma, "Expected '{' before ',' in bib-entry-bytes."

    citekey_B = entry_B[pos_brace + 1 : pos_comma]
    citekey_B = bytes.strip(citekey_B)
    return citekey_B


def _parse_fields_bytes(entry_B):
    assert entry_B[-1] == b"}"[0]

    pos_brace = bytes.find(entry_B, b"{")
    pos_comma = bytes.find(entry_B, b",")
    pos_equal = bytes.find(entry_B, b"=")

    assert pos_brace >= 0, "Expected '{' in bib-entry-bytes."
    assert pos_equal >= 0, "Expected '=' in bib-entry-bytes."
    assert pos_brace < pos_equal, "Expected '{' before '=' in bib-entry-bytes."

    if pos_brace < pos_comma < pos_equal:
        # thie entry has a citekey
        split = pos_comma
    else:
        split = pos_brace

    fields_B = entry_B[split + 1 : -1]

    return fields_B


def _parse_preamble_bytes(entry_B):
    start, stop = _find_braces_start_stop(B=entry_B,)
    preamble_B = entry_B[start + 1 : stop]
    return bytes.strip(preamble_B)


def _parse_fields_into_dict(fields_B):
    work = bytes(fields_B)

    fields = {}
    while True:
        pos = bytes.find(work, b"=")
        if pos == -1:
            break
        key = work[0:pos]
        key = bytes.replace(key, b",", b"")
        key = bytes.replace(key, b" ", b"")

        work = work[pos + 1 :]
        start = _find_first_non_space(work)
        work = work[start:]

        if bytes.isdigit(work[0:1]):
            # a digit value
            stop = _find_first_non_digit(work)
            value = int(work[0:stop])
        elif work[0:1] == b"{":
            # is value in braces
            start, stop = _find_braces_start_stop(
                B=work, opening=b"{", closing=b"}"
            )
            assert start == 0
            value = work[1:stop]
        elif work[0:1] == b'"':
            # is value in quotes
            stop = _find_first_quote_not_escaped(work)
            value = work[1:stop]
        else:
            assert False, (
                "Expected value in braces '{}', quotes '" "', or as digit."
            )

        work = work[stop + 1 :]

        fields[key] = value
    return fields


def _strip_latex(B):
    """
    Returns bytes without leading, trailing, or consecutive whitespaces.
    """
    out = bytes.strip(B)
    return b" ".join(out.split())


def _advance(B, pos):
    """
    Returns byts overwritten with whitespaces up to and including 'pos'.
    """
    m = pos + 1
    assert m >= 0  # prevent index looping
    assert pos < len(B)
    return bytes.join(b"", [m * b" ", B[m:]])


def _decode_ascii(B):
    """
    Decode B to ascii and print B in case of errors.
    """
    try:
        asc = bytes.decode(B, encoding="ascii", errors="strict")
        return asc
    except Exception as err:
        print("Can not decode: ", B)
        raise err


def _find_braces_start_stop(B, opening=b"{", closing=b"}"):
    """
    Returns the start and stop position of the outermost pair of
    opening and closing braces.
    """
    work = bytes(B)
    pos = bytes.find(work, opening)
    if pos < 0:
        return -1, -1
    num_open = 1
    work = _advance(B=work, pos=pos)
    start = int(pos)

    while num_open != 0:
        next_open = bytes.find(work, opening)
        next_closing = bytes.find(work, closing)

        if next_open >= 0 and next_closing >= 0:
            if next_open < next_closing:
                num_open += 1
                pos = next_open
            else:
                num_open -= 1
                pos = next_closing
            work = _advance(B=work, pos=pos)
            continue
        if next_open >= 0:
            assert False, "Expected more braces to close before end of bytes"
        if next_closing >= 0:
            num_open -= 1
            pos = next_closing
            work = _advance(B=work, pos=pos)
            continue
        assert False, "Expected some braces in bytes before end."
    return start, pos


def _find_first_non_space(B):
    """
    Returns the position of the first char that is no whitespace.
    """
    pos = 0
    while pos < len(B):
        if not bytes.isspace(B[pos : pos + 1]):
            return pos
        else:
            pos += 1
    return -1


def _find_first_non_digit(B):
    """
    Returns the position of the first char that is no digit.
    """
    pos = 0
    while pos < len(B):
        if not bytes.isdigit(B[pos : pos + 1]):
            return pos
        else:
            pos += 1
    return -1


def _brace_balance(B):
    """
    Returns a list where each character in B is assigned the brace-balance.
    """
    brace_balance = []
    bal = 0
    for p in range(len(B)):
        if B[p : p + 1] == b"{":
            bal += 1
        elif B[p : p + 1] == b"}":
            bal -= 1
        brace_balance.append(int(bal))
    return brace_balance


def _find_first_quote_not_escaped(B):
    """
    Returns the position of the first quote '"' that is not escaped by either
    '\\"' or with braces {"}.
    """
    if len(B) == 0:
        return -1

    if len(B) == 1:
        if B[0:1] == b'"':
            return 0
        else:
            return -1
    brace_balance = _brace_balance(B)
    for p in range(len(B) - 1):
        if B[p + 1 : p + 2] == b'"':
            if B[p + 0 : p + 1] == b"\\":
                pass
            else:
                if brace_balance[p + 1] == 0:
                    return p + 1
                else:
                    pass
    return -1
