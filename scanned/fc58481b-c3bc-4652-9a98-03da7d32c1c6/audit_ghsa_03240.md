# [H] HTTP Request Smuggling in reel

## Summary
Severity: High
Advisory: GHSA-x3v4-pxvm-63j8
CVE: CVE-2020-7659
CWE: CWE-444
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-05-24
Source: https://github.com/advisories/GHSA-x3v4-pxvm-63j8
Type: github-advisory

## Affected
- RubyGems: `reel` — affected >=0

## Details
reel through 0.6.1 allows Request Smuggling attacks due to incorrect Content-Length and Transfer encoding header parsing. It is possible to conduct HTTP request smuggling attacks by sending the Content-Length header twice. Furthermore, invalid Transfer Encoding headers were found to be parsed as valid which could be leveraged for TECL smuggling attacks. Note, This project is deprecated, and is not maintained any more.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7659
- https://github.com/celluloid/reel
- https://snyk.io/vuln/SNYK-RUBY-REEL-569135
