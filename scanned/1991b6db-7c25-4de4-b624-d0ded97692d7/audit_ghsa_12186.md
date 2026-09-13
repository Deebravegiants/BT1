# [H] Arbitrary file read vulnerability in yard server

## Summary
Severity: High
Advisory: GHSA-gj4p-3wh3-2rmf
CVE: CVE-2017-17042
CWE: CWE-22
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2017-12-21
Source: https://github.com/advisories/GHSA-gj4p-3wh3-2rmf
Type: github-advisory

## Affected
- RubyGems: `yard` — affected >=0 <0.9.11

## Details
`lib/yard/core_ext/file.rb` in the server in YARD before 0.9.11 does not block relative paths with an initial `../` sequence, which allows attackers to conduct directory traversal attacks and read arbitrary files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-17042
- https://github.com/lsegal/yard/commit/b0217b3e30dc53d057b1682506333335975e62b4
- https://github.com/advisories/GHSA-gj4p-3wh3-2rmf
- https://github.com/lsegal/yard
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/yard/CVE-2017-17042.yml
