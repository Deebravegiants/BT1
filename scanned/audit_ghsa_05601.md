# [M] Active Job - Object injection security vulnerability

## Summary
Severity: Medium
Advisory: GHSA-mpwp-4h2m-765c
CWE: CWE-74
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-01-16
Source: https://github.com/advisories/GHSA-mpwp-4h2m-765c
Type: github-advisory

## Affected
- RubyGems: `activejob` — affected >=0 <4.2.0.beta2

## Details
Active Job vulnerability: An Active Job bug allowed String arguments to be deserialized as if they were Global IDs, an object injection security vulnerability.

## References
- https://advisories.gitlab.com/pkg/gem/activejob/OSVDB-112347
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activejob/GHSA-mpwp-4h2m-765c.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activejob/OSVDB-112347.yml
