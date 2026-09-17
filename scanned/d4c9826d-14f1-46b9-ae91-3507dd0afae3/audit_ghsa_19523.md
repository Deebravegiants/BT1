# [H] Whoogle allows attackers to execute arbitrary code via supplying a crafted search query

## Summary
Severity: High
Advisory: GHSA-2689-cw26-6cpj
CVE: CVE-2024-53305
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-04-16
Source: https://github.com/advisories/GHSA-2689-cw26-6cpj
Type: github-advisory

## Affected
- PyPI: `whoogle-search` — affected >=0 <0.9.1

## Details
An issue in the component /models/config.py of Whoogle search v0.9.0 allows attackers to execute arbitrary code via supplying a crafted search query.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-53305
- https://github.com/benbusby/whoogle-search/commit/223f00c3c0533423114f99b30c561278bc0b42ba
- https://fern89.github.io/posts/whoogle-rce
- https://gist.github.com/fern89/ca5fe76ad81b4bc363e7341e523a1651
- https://github.com/benbusby/whoogle-search
