# [M] pypdf: Possible large memory usage for form XObjects during text extraction

## Summary
Severity: Medium
Advisory: GHSA-j543-4vmf-qm7v
CVE: CVE-2026-49461
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-j543-4vmf-qm7v
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.12.2

## Details
### Impact
An attacker who uses this vulnerability can craft a PDF which leads to large memory usage. This requires extracting the text of a page which contains a form XObject with self-references.

### Patches
This has been fixed in [pypdf==6.12.2](https://github.com/py-pdf/pypdf/releases/tag/6.12.2).

### Workarounds
If you cannot upgrade yet, consider applying the changes from PR [#3805](https://github.com/py-pdf/pypdf/pull/3805).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-j543-4vmf-qm7v
- https://github.com/py-pdf/pypdf/pull/3805
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.12.2
