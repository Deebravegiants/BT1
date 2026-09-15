# [M] pypdf possibly loops infinitely when reading DCT inline images without EOF marker

## Summary
Severity: Medium
Advisory: GHSA-vr63-x8vc-m265
CVE: CVE-2025-62707
CWE: CWE-834
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-10-22
Source: https://github.com/advisories/GHSA-vr63-x8vc-m265
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.1.3

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to an infinite loop. This requires parsing the content stream of a page which has an inline image using the DCTDecode filter.

### Patches
This has been fixed in [pypdf==6.1.3](https://github.com/py-pdf/pypdf/releases/tag/6.1.3).

### Workarounds
If you cannot upgrade yet, consider applying the changes from PR [#3501](https://github.com/py-pdf/pypdf/pull/3501).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-vr63-x8vc-m265
- https://nvd.nist.gov/vuln/detail/CVE-2025-62707
- https://github.com/py-pdf/pypdf/pull/3501
- https://github.com/py-pdf/pypdf/commit/f2864d6dd9bac7cecd3f4f54308b25ebbfa178f8
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.1.3
