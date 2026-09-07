# [M] pypdf vulnerable to inefficient decoding of ASCIIHexDecode streams

## Summary
Severity: Medium
Advisory: GHSA-9m86-7pmv-2852
CVE: CVE-2026-28804
CWE: CWE-407
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-9m86-7pmv-2852
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.7.5

## Details
### Impact
An attacker who uses this vulnerability can craft a PDF which leads to long runtimes. This requires accessing a stream which uses the `/ASCIIHexDecode` filter.

### Patches
This has been fixed in [pypdf==6.7.5](https://github.com/py-pdf/pypdf/releases/tag/6.7.5).

### Workarounds
If you cannot upgrade yet, consider applying the changes from PR [#3666](https://github.com/py-pdf/pypdf/pull/3666).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-9m86-7pmv-2852
- https://nvd.nist.gov/vuln/detail/CVE-2026-28804
- https://github.com/py-pdf/pypdf/pull/3666
- https://github.com/py-pdf/pypdf/commit/648c627d2657447dfb1773412af05a0a5103b98f
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.7.5
