# [M] RubyGems Regular Expression Denial of Service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9j7m-rjqx-48vh
CVE: CVE-2013-4287
CWE: CWE-400
Ecosystem: RubyGems
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-9j7m-rjqx-48vh
Type: github-advisory

## Affected
- RubyGems: `rubygems-update` — affected >=0 <1.8.23.1
- RubyGems: `rubygems-update` — affected >=1.8.24 <1.8.26
- RubyGems: `rubygems-update` — affected >=2.0.0 <2.0.8
- RubyGems: `rubygems-update` — affected >=2.1.0.rc.1 <2.1.0

## Details
Algorithmic complexity vulnerability in Gem::Version::VERSION_PATTERN in `lib/rubygems/version.rb` in RubyGems before 1.8.23.1, 1.8.24 through 1.8.25, 2.0.x before 2.0.8, and 2.1.x before 2.1.0, as used in Ruby 1.9.0 through 2.0.0p247, allows remote attackers to cause a denial of service (CPU consumption) via a crafted gem version that triggers a large amount of backtracking in a regular expression.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4287
- https://github.com/rubygems/rubygems/commit/938a7e31ac73655845ab9045629ff3f580a125da
- https://github.com/rubygems/rubygems/commit/b697536f2455e8c8853cf5cf8a1017a36031ed67
- https://github.com/rubygems/rubygems/commit/b9baec03145aed684d1cd3c87dcac3cc06becd9b
- https://github.com/rubygems/rubygems/commit/ed733bc379d75620f5be4213f89d1d7b38be3191
- https://github.com/rubygems/rubygems/blob/03a074e8838683f45611b119fd8f363aa44fe2fd/CHANGELOG.md
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rubygems-update/CVE-2013-4287.yml
- https://web.archive.org/web/20160806152839/https://puppet.com/security/cve/cve-2013-4287
- http://blog.rubygems.org/2013/09/09/CVE-2013-4287.html
- http://rhn.redhat.com/errata/RHSA-2013-1427.html
- http://rhn.redhat.com/errata/RHSA-2013-1441.html
- http://rhn.redhat.com/errata/RHSA-2013-1523.html
- http://rhn.redhat.com/errata/RHSA-2013-1852.html
- http://rhn.redhat.com/errata/RHSA-2014-0207.html
- http://www.openwall.com/lists/oss-security/2013/09/10/1
