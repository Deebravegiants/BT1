# [M] pypdf: Manipulated RunLengthDecode streams can exhaust RAM

## Summary
Severity: Medium
Advisory: GHSA-f2v5-7jq9-h8cg
CVE: CVE-2026-28351
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-28
Source: https://github.com/advisories/GHSA-f2v5-7jq9-h8cg
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.7.4

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to large memory usage. This requires parsing the content stream using the RunLengthDecode filter.

### Patches
This has been fixed in [pypdf==6.7.4](https://github.com/py-pdf/pypdf/releases/tag/6.7.4).

### Workarounds
If you cannot upgrade yet, consider applying the changes from PR [#3664](https://github.com/py-pdf/pypdf/pull/3664).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-f2v5-7jq9-h8cg
- https://nvd.nist.gov/vuln/detail/CVE-2026-28351
- https://github.com/py-pdf/pypdf/pull/3664
- https://github.com/py-pdf/pypdf/commit/f309c6003746414dc7b5048c19e6d879ff2dc858
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.7.4
