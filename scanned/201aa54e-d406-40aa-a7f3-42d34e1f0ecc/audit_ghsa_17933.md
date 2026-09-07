# [M] Active Record logging vulnerable to ANSI escape injection

## Summary
Severity: Medium
Advisory: GHSA-76r7-hhxj-r776
CVE: CVE-2025-55193
CWE: CWE-150
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-13
Source: https://github.com/advisories/GHSA-76r7-hhxj-r776
Type: github-advisory

## Affected
- RubyGems: `activerecord` — affected >=8.0 <8.0.2.1
- RubyGems: `activerecord` — affected >=7.2 <7.2.2.2
- RubyGems: `activerecord` — affected >=0 <7.1.5.2

## Details
This vulnerability has been assigned the CVE identifier CVE-2025-55193

### Impact
The ID passed to `find` or similar methods may be logged without escaping. If this is directly to the terminal it may include unescaped ANSI sequences.

### Releases
The fixed releases are available at the normal locations.

### Credits

Thanks to [lio346](https://hackerone.com/lio346) from Unit 515 of OPSWAT for reporting this vulnerability

## References
- https://github.com/rails/rails/security/advisories/GHSA-76r7-hhxj-r776
- https://nvd.nist.gov/vuln/detail/CVE-2025-55193
- https://github.com/rails/rails/commit/3beef20013736fd52c5dcfdf061f7999ba318290
- https://github.com/rails/rails/commit/568c0bc2f1e74c65d150a84b89a080949bf9eb9b
- https://github.com/rails/rails/commit/6a944ca4805e72050a0fbb1a461534eb760d3202
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activerecord/CVE-2025-55193.yml
