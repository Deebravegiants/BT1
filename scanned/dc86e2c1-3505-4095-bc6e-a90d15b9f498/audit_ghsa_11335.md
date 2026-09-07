# [M] PyMuPDF has a path traversal in _main_.py

## Summary
Severity: Medium
Advisory: GHSA-cxqh-p2w9-fmr7
CVE: CVE-2026-3029
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-cxqh-p2w9-fmr7
Type: github-advisory

## Affected
- PyPI: `PyMuPDF` — affected >=1.26.5 <1.26.7

## Details
A path traversal and arbitrary file write vulnerability exist in the embedded get function in '_main_.py' in PyMuPDF version, 1.26.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3029
- https://github.com/pymupdf/PyMuPDF
- https://www.kb.cert.org/vuls/id/504749
- http://github.com/pymupdf/PyMuPDF
- http://github.com/pymupdf/PyMuPDF/commit/603cafe38a183b8bab34f16d05043b4185d8d40a
