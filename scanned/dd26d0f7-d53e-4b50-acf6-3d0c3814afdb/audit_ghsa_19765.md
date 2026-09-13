# [M] mavo DOM Clobbering vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3mf5-r4hg-hfx9
CVE: CVE-2024-53388
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-03-03
Source: https://github.com/advisories/GHSA-3mf5-r4hg-hfx9
Type: github-advisory

## Affected
- npm: `mavo` — affected >=0

## Details
A DOM Clobbering vulnerability in mavo v0.3.2 allows attackers to execute arbitrary code via supplying a crafted HTML element.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-53388
- https://gist.github.com/jackfromeast/a61a5429a97985e7ff4c1d39e339d5d8
- https://github.com/mavoweb/mavo
