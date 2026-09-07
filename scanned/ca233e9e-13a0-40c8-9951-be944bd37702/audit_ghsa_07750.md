# [M] pypdf possibly has long runtimes for malformed FlateDecode streams

## Summary
Severity: Medium
Advisory: GHSA-9mvc-8737-8j8h
CVE: CVE-2026-27026
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-9mvc-8737-8j8h
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.7.1

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to long runtimes. This requires a malformed `/FlateDecode` stream, where the byte-by-byte decompression is used.

### Patches

This has been fixed in [pypdf==6.7.1](https://github.com/py-pdf/pypdf/releases/tag/6.7.1).

### Workarounds

If you cannot upgrade yet, consider applying the changes from PR [#3644](https://github.com/py-pdf/pypdf/pull/3644).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-9mvc-8737-8j8h
- https://nvd.nist.gov/vuln/detail/CVE-2026-27026
- https://github.com/py-pdf/pypdf/pull/3644
- https://github.com/py-pdf/pypdf/commit/7905842d833f899f1d3228af7e7467ad80277016
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.7.1
