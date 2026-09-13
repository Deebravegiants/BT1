# [M] pypdf: Manipulated FlateDecode XFA streams can exhaust RAM

## Summary
Severity: Medium
Advisory: GHSA-x7hp-r3qg-r3cj
CVE: CVE-2026-27888
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-x7hp-r3qg-r3cj
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.7.3

## Details
### Impact
An attacker who uses this vulnerability can craft a PDF which leads to the RAM being exhausted. This requires accessing the `xfa` property of a reader or writer and the corresponding stream being compressed using `/FlateDecode`.

### Patches
This has been fixed in [pypdf==6.7.3](https://github.com/py-pdf/pypdf/releases/tag/6.7.3).

### Workarounds
If projects cannot upgrade yet, consider applying the changes from PR [#3658](https://github.com/py-pdf/pypdf/pull/3658).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-x7hp-r3qg-r3cj
- https://nvd.nist.gov/vuln/detail/CVE-2026-27888
- https://github.com/py-pdf/pypdf/pull/3658
- https://github.com/py-pdf/pypdf/commit/7a4c8246ed48d9d328fb596942271da47b6d109c
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.7.3
