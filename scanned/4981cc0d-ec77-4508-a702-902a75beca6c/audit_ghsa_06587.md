# [M] pypdf: Possible long runtimes for repeated malformed cross-reference entries 

## Summary
Severity: Medium
Advisory: GHSA-55h5-xmcq-c37v
CVE: CVE-2026-59937
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-23
Source: https://github.com/advisories/GHSA-55h5-xmcq-c37v
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.14.0

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to long runtimes. This requires cross-reference streams with repeated malformed cross-reference streams.

### Patches

This has been fixed in [pypdf==6.14.0](https://github.com/py-pdf/pypdf/releases/tag/6.14.0).

### Workarounds

If you cannot upgrade yet, consider applying the changes from PR [#3887](https://github.com/py-pdf/pypdf/pull/3887).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-55h5-xmcq-c37v
- https://nvd.nist.gov/vuln/detail/CVE-2026-59937
- https://github.com/py-pdf/pypdf/pull/3887
- https://github.com/py-pdf/pypdf/commit/b5fc5aa714f4b696fb9b1deaa35a9e4a4eb50dae
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.14.0
