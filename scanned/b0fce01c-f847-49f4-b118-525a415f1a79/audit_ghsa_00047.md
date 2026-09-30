# [M] Gyazo allows local users to write arbitrary files

## Summary
Severity: Medium
Advisory: GHSA-6x45-86q6-rcmr
CVE: CVE-2014-4994
CWE: CWE-20
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-01-22
Source: https://github.com/advisories/GHSA-6x45-86q6-rcmr
Type: github-advisory

## Affected
- RubyGems: `gyazo` — affected >=1.0.0 <2.0.0

## Details
`lib/gyazo/client.rb` in the gyazo gem 1.0.0 for Ruby allows local users to write to arbitrary files via a symlink attack on a temporary file, related to time-based filenames.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-4994
- https://github.com/gyazo/gyazo-ruby
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/gyazo/CVE-2014-4994.yml
- https://web.archive.org/web/20200229061943/http://www.vapid.dhs.org/advisories/gyazo-1.0.0.html
- http://www.openwall.com/lists/oss-security/2014/07/07/13
- http://www.openwall.com/lists/oss-security/2014/07/17/5
