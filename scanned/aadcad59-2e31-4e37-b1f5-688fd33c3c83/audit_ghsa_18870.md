# [M] pypdf can exhaust RAM via manipulated LZWDecode streams

## Summary
Severity: Medium
Advisory: GHSA-jfx9-29x2-rv3j
CVE: CVE-2025-62708
CWE: CWE-409
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-10-22
Source: https://github.com/advisories/GHSA-jfx9-29x2-rv3j
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.1.3

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to large memory usage. This requires parsing the content stream of a page using the LZWDecode filter.

### Patches
This has been fixed in [pypdf==6.1.3](https://github.com/py-pdf/pypdf/releases/tag/6.1.3).

### Workarounds
If you cannot upgrade yet, consider applying the changes from PR [#3502](https://github.com/py-pdf/pypdf/pull/3502).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-jfx9-29x2-rv3j
- https://nvd.nist.gov/vuln/detail/CVE-2025-62708
- https://github.com/py-pdf/pypdf/pull/3502
- https://github.com/py-pdf/pypdf/commit/e51d07807ffcdaf18077b9486dadb3dc05b368da
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.1.3
