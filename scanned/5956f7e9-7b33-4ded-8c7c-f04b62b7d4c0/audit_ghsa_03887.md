# [M] The rack-cors rubygem may allow directory traveral

## Summary
Severity: Medium
Advisory: GHSA-pf8f-w267-mq2h
CVE: CVE-2019-18978
CWE: CWE-22
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-11-15
Source: https://github.com/advisories/GHSA-pf8f-w267-mq2h
Type: github-advisory

## Affected
- RubyGems: `rack-cors` — affected >=0 <1.0.4

## Details
An issue was discovered in the rack-cors (aka Rack CORS Middleware) gem before 1.0.4 for Ruby. It allows ../ directory traversal to access private resources because resource matching does not ensure that pathnames are in a canonical format.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18978
- https://github.com/cyu/rack-cors/commit/e4d4fc362a4315808927011cbe5afcfe5486f17d
- https://github.com/cyu/rack-cors
- https://github.com/cyu/rack-cors/compare/v1.0.3...v1.0.4
- https://lists.debian.org/debian-lts-announce/2020/02/msg00004.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00000.html
- https://usn.ubuntu.com/4571-1
- https://www.debian.org/security/2021/dsa-4918
