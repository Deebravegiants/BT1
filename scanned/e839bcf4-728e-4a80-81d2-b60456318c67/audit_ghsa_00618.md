# [M] Sinatra Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-h29f-7f56-j8wh
CVE: CVE-2018-7212
CWE: CWE-22
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2018-02-20
Source: https://github.com/advisories/GHSA-h29f-7f56-j8wh
Type: github-advisory

## Affected
- RubyGems: `sinatra` — affected >=2.0.0.beta1 <2.0.1

## Details
An issue was discovered in `rack-protection/lib/rack/protection/path_traversal.rb` in Sinatra 2.x before 2.0.1 on Windows. Path traversal is possible via backslash characters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7212
- https://github.com/sinatra/sinatra/pull/1379
- https://github.com/sinatra/sinatra/commit/6ad721abcfe36334108dcdd05d046c361e1b7a9c
- https://github.com/sinatra/sinatra
