# [M] Array data injection vulnerability in activerecord

## Summary
Severity: Medium
Advisory: GHSA-hqf9-rc9j-5fmj
CVE: CVE-2014-0080
CWE: CWE-89
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-hqf9-rc9j-5fmj
Type: github-advisory

## Affected
- RubyGems: `activerecord` — affected >=4.0.0 <4.0.3
- RubyGems: `activerecord` — affected >=4.1.0.beta1 <4.1.0.beta2

## Details
SQL injection vulnerability in `activerecord/lib/active_record/connection_adapters/postgresql/cast.rb` in Active Record in Ruby on Rails 4.0.x before 4.0.3, and 4.1.0.beta1, when PostgreSQL is used, allows remote attackers to execute "add data" SQL commands via vectors involving `\` (backslash) characters that are not properly handled in operations on array columns.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0080
- https://github.com/advisories/GHSA-hqf9-rc9j-5fmj
- https://github.com/rails/rails/tree/main/activerecord
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activerecord/CVE-2014-0080.yml
- https://web.archive.org/web/20210301004521/https://groups.google.com/forum/message/raw?msg=rubyonrails-security/Wu96YkTUR6s/pPLBMZrlwvYJ
- http://openwall.com/lists/oss-security/2014/02/18/9
