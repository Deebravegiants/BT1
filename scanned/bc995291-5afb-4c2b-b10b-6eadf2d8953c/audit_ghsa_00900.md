# [M] Remote Memory Exposure in bl

## Summary
Severity: Medium
Advisory: GHSA-pp7h-53gx-mx7r
CVE: CVE-2020-8244
CWE: CWE-125, CWE-126
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-pp7h-53gx-mx7r
Type: github-advisory

## Affected
- npm: `bl` — affected >=0 <1.2.3
- npm: `bl` — affected >=2.0.0 <2.2.1
- npm: `bl` — affected >=3.0.0 <3.0.1
- npm: `bl` — affected >=4.0.0 <4.0.3

## Details
A buffer over-read vulnerability exists in bl <4.0.3, <3.0.1, <2.2.1, and <1.2.3 which could allow an attacker to supply user input (even typed) that if it ends up in consume() argument and can become negative, the BufferList state can be corrupted, tricking it into exposing uninitialized memory via regular .slice() calls.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8244
- https://github.com/rvagg/bl/commit/8a8c13c880e2bef519133ea43e0e9b78b5d0c91e
- https://github.com/rvagg/bl/commit/d3e240e3b8ba4048d3c76ef5fb9dd1f8872d3190
- https://github.com/rvagg/bl/commit/dacc4ac7d5fcd6201bcf26fbd886951be9537466
- https://hackerone.com/reports/966347
- https://lists.debian.org/debian-lts-announce/2021/06/msg00028.html
