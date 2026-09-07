# [H] activesupport in Rails vulnerable to incorrect data conversion

## Summary
Severity: High
Advisory: GHSA-xgr2-v94m-rc9g
CVE: CVE-2013-0333
CWE: CWE-74
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-xgr2-v94m-rc9g
Type: github-advisory

## Affected
- RubyGems: `activesupport` — affected >=2.3.2 <2.3.16
- RubyGems: `activesupport` — affected >=3.0.0 <3.0.20

## Details
`lib/active_support/json/backends/yaml.rb` in Ruby on Rails 2.3.x before 2.3.16 and 3.0.x before 3.0.20 does not properly convert JSON data to YAML data for processing by a YAML parser, which allows remote attackers to execute arbitrary code, conduct SQL injection attacks, or bypass authentication via crafted data that triggers unsafe decoding, a different vulnerability than CVE-2013-0156.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-0333
- https://access.redhat.com/errata/RHSA-2013:0201
- https://access.redhat.com/errata/RHSA-2013:0202
- https://access.redhat.com/errata/RHSA-2013:0203
- https://access.redhat.com/security/cve/CVE-2013-0333
- https://bugzilla.redhat.com/show_bug.cgi?id=903440
- https://github.com/advisories/GHSA-xgr2-v94m-rc9g
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activesupport/CVE-2013-0333.yml
- https://groups.google.com/forum/?fromgroups=#!topic/rubyonrails-security/1h2DR63ViGo
- https://groups.google.com/group/rubyonrails-security/msg/52179af76915e518?dmode=source&output=gplain
- https://puppet.com/security/cve/cve-2013-0333
- http://lists.apple.com/archives/security-announce/2013/Jun/msg00000.html
- http://lists.apple.com/archives/security-announce/2013/Mar/msg00002.html
- http://rhn.redhat.com/errata/RHSA-2013-0201.html
- http://rhn.redhat.com/errata/RHSA-2013-0202.html
- http://rhn.redhat.com/errata/RHSA-2013-0203.html
- http://support.apple.com/kb/HT5784
- http://weblog.rubyonrails.org/2013/1/28/Rails-3-0-20-and-2-3-16-have-been-released
- http://www.debian.org/security/2013/dsa-2613
- http://www.kb.cert.org/vuls/id/628463
