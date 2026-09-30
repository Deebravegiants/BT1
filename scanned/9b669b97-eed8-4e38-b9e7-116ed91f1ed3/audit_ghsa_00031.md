# [H] Improper Access Control in activejob

## Summary
Severity: High
Advisory: GHSA-q2qw-rmrh-vv42
CVE: CVE-2018-16476
CWE: CWE-284, CWE-502
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-12-05
Source: https://github.com/advisories/GHSA-q2qw-rmrh-vv42
Type: github-advisory

## Affected
- RubyGems: `activejob` — affected >=4.2.0 <4.2.11
- RubyGems: `activejob` — affected >=5.0.0 <5.0.7.1
- RubyGems: `activejob` — affected >=5.1.0 <5.1.6.1
- RubyGems: `activejob` — affected >=5.2.0 <5.2.1.1

## Details
A Broken Access Control vulnerability in Active Job versions >= 4.2.0 allows an attacker to craft user input which can cause Active Job to deserialize it using GlobalId and give them access to information that they should not have.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16476
- https://github.com/rails/rails/commit/970b0d754be7c71a760d9b807eea32297fd838e3
- https://access.redhat.com/errata/RHSA-2019:0600
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activejob/CVE-2018-16476.yml
- https://groups.google.com/d/msg/rubyonrails-security/FL4dSdzr2zw/zjKVhF4qBAAJ
- https://groups.google.com/forum/#!topic/rubyonrails-security/FL4dSdzr2zw
- https://weblog.rubyonrails.org/2018/11/27/Rails-4-2-5-0-5-1-5-2-have-been-released
