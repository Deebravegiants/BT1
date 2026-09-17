# [M] pypdf and PyPDF2 possible Infinite Loop when a comment isn't followed by a character

## Summary
Severity: Medium
Advisory: GHSA-4vvm-4w3v-6mr8
CVE: CVE-2023-36464
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-30
Source: https://github.com/advisories/GHSA-4vvm-4w3v-6mr8
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=3.1.0 <3.9.0
- PyPI: `PyPDF2` — affected >=2.2.0

## Details
### Impact
An attacker who uses this vulnerability can craft a PDF which leads to an infinite loop if `__parse_content_stream` is executed. This infinite loop blocks the current process and can utilize a single core of the CPU by 100%. It does not affect memory usage. That is, for example, the case if the user extracted text from such a PDF.

Example Code and a PDF that causes the issue:

```python
from pypdf import PdfReader

# https://objects.githubusercontent.com/github-production-repository-file-5c1aeb/3119517/11367871?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20230627%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20230627T201018Z&X-Amz-Expires=300&X-Amz-Signature=d71c8fd9181c4875f0c04d563b6d32f1d4da6e7b2e6be2f14479ce4ecdc9c8b2&X-Amz-SignedHeaders=host&actor_id=1658117&key_id=0&repo_id=3119517&response-content-disposition=attachment%3Bfilename%3DMiFO_LFO_FEIS_NOA_Published.3.pdf&response-content-type=application%2Fpdf
reader = PdfReader("MiFO_LFO_FEIS_NOA_Published.3.pdf")
page = reader.pages[0]
page.extract_text()
```

The issue was introduced with https://github.com/py-pdf/pypdf/pull/969

### Patches

The issue was fixed with https://github.com/py-pdf/pypdf/pull/1828

### Workarounds

It is recommended to upgrade to `pypdf>=3.9.0`. PyPDF2 users should migrate to pypdf.

If you cannot update your version of pypdf, you should modify `pypdf/generic/_data_structures.py`:

```
OLD: while peek not in (b"\r", b"\n"):
NEW: while peek not in (b"\r", b"\n", b""):
```

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-4vvm-4w3v-6mr8
- https://nvd.nist.gov/vuln/detail/CVE-2023-36464
- https://github.com/py-pdf/pypdf/pull/1828
- https://github.com/py-pdf/pypdf/pull/969
- https://github.com/py-pdf/pypdf/commit/b0e5c689df689ab173df84dacd77b6fc3c161932
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/3.9.0
