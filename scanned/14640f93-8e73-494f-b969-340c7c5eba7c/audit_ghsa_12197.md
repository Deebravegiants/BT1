# [H] Active Record contains SQL Injection via improper range quoting

## Summary
Severity: High
Advisory: GHSA-r8fh-hq2p-7qhq
CVE: CVE-2014-3483
CWE: CWE-89
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-r8fh-hq2p-7qhq
Type: github-advisory

## Affected
- RubyGems: `activerecord` — affected >=4.0.0 <4.0.7
- RubyGems: `activerecord` — affected >=4.1.0 <4.1.3

## Details
SQL injection vulnerability in activerecord/lib/active_record/connection_adapters/postgresql/quoting.rb in the PostgreSQL adapter for Active Record in Ruby on Rails 4.x before 4.0.7 and 4.1.x before 4.1.3 allows remote attackers to execute arbitrary SQL commands by leveraging improper range quoting.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3483
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activerecord/CVE-2014-3483.yml
- https://groups.google.com/forum/message/raw?msg=rubyonrails-security/wDxePLJGZdI/WP7EasCJTA4J
- https://web.archive.org/web/20200228150648/http://www.securityfocus.com/bid/68341
- http://openwall.com/lists/oss-security/2014/07/02/5
- http://rhn.redhat.com/errata/RHSA-2014-0877.html
- http://www.debian.org/security/2014/dsa-2982
