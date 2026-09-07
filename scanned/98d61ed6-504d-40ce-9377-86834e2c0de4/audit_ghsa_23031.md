# [M] MapProxy vulnerable to cross-site scripting in demo service

## Summary
Severity: Medium
Advisory: GHSA-g4rw-82hq-8jpr
CVE: CVE-2017-1000426
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-g4rw-82hq-8jpr
Type: github-advisory

## Affected
- PyPI: `MapProxy` — affected >=0 <1.11.1

## Details
MapProxy version 1.11.1 and older are vulnerable to cross-site scripting in the demo service resulting in possible information disclosure. An incomplete fix was released in v[1.10.4](https://github.com/mapproxy/mapproxy/issues/322#issuecomment-518573169), and a complete fix was released in v[1.11.1](https://github.com/mapproxy/mapproxy/commit/436c8f489761d1b4ee22b2440b53cc96bbc28aea).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000426
- https://github.com/mapproxy/mapproxy/issues/322
- https://github.com/mapproxy/mapproxy/commit/420412aad45171e05752007a0a2350c03c28dfd8
- https://github.com/mapproxy/mapproxy/commit/436c8f489761d1b4ee22b2440b53cc96bbc28aea
- https://github.com/mapproxy/mapproxy
