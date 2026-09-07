# [M] pypdf: Possible long runtimes/large memory usage for large CID font width ranges

## Summary
Severity: Medium
Advisory: GHSA-fwg2-594c-jp42
CVE: CVE-2026-71852
CWE: CWE-834
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-fwg2-594c-jp42
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.15.0

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to long runtimes and large memory consumption. This requires parsing the font width entries of a font with unusually large values, for example during text extraction.

### Patches

This has been fixed in [pypdf==6.15.0](https://github.com/py-pdf/pypdf/releases/tag/6.15.0).

### Workarounds

If you cannot upgrade yet, consider applying the changes from PR [#3946](https://github.com/py-pdf/pypdf/pull/3946).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-fwg2-594c-jp42
- https://github.com/py-pdf/pypdf/pull/3946
- https://github.com/py-pdf/pypdf/commit/51cb6acf9e8a35b77e90b4d87d28fe3e1416d7d7
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.15.0
