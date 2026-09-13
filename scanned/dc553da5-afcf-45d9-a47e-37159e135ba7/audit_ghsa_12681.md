# [M] PyPDF2 vulnerable to possible Infinite Loop when reading malformed objects

## Summary
Severity: Medium
Advisory: GHSA-hm9v-vj3r-r55m
CVE: CVE-2023-36807
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-30
Source: https://github.com/advisories/GHSA-hm9v-vj3r-r55m
Type: github-advisory

## Affected
- PyPI: `PyPDF2` — affected >=2.10.5 <2.10.6

## Details
### Impact
An attacker who uses this vulnerability can craft a PDF which leads to an infinite loop.
This infinite loop blocks the current process and can utilize a single core of the CPU by 100%. It does not affect memory usage. That is, for example, the case if the user extracted metadata from such a malformed PDF.

### Patches
The issue was fixed with https://github.com/py-pdf/pypdf/pull/1331

### Workarounds
If you cannot update your version of `PyPDF2` (preferably to `pypdf>3.1.0` as PyPDF2 is deprecated), you should modify `PyPDF2/generic/_data_structures.py::read_object`.

Replace:

```python
    else:
        # number object OR indirect reference
        peek = stream.read(20)
        stream.seek(-len(peek), 1)  # reset to start
        if IndirectPattern.match(peek) is not None:
            return IndirectObject.read_from_stream(stream, pdf)
        else:
            return NumberObject.read_from_stream(stream)
```

by

```python
    elif tok in b"0123456789+-.":
        # number object OR indirect reference
        peek = stream.read(20)
        stream.seek(-len(peek), 1)  # reset to start
        if IndirectPattern.match(peek) is not None:
            return IndirectObject.read_from_stream(stream, pdf)
        else:
            return NumberObject.read_from_stream(stream)
    else:
        raise PdfReadError(
            f"Invalid Elementary Object starting with {tok} @{stream.tell()}"
        )
```

### References
* [pypdf issue #1329](https://github.com/py-pdf/pypdf/issues/1329)
* [pypdf PR #1331](https://github.com/py-pdf/pypdf/pull/1331)

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-hm9v-vj3r-r55m
- https://nvd.nist.gov/vuln/detail/CVE-2023-36807
- https://github.com/py-pdf/pypdf/issues/1329
- https://github.com/py-pdf/pypdf/pull/1331
- https://github.com/py-pdf/pypdf/commit/e6531a25325e7e0174b6a1ba03b57320b5227f6b
- https://github.com/py-pdf/pypdf
