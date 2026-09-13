# [H] Active Record subject to strong parameters protection bypass

## Summary
Severity: High
Advisory: GHSA-9rf5-jm6f-2fmm
CVE: CVE-2014-3514
CWE: CWE-284
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-9rf5-jm6f-2fmm
Type: github-advisory

## Affected
- RubyGems: `activerecord` — affected >=4.0.0 <4.0.9
- RubyGems: `activerecord` — affected >=4.1.0 <4.1.5

## Details
`activerecord/lib/active_record/relation/query_methods.rb` in Active Record in Ruby on Rails 4.0.x before 4.0.9 and 4.1.x before 4.1.5 allows remote attackers to bypass the strong parameters protection mechanism via crafted input to an application that makes `create_with` calls.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3514
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activerecord/CVE-2014-3514.yml
- https://groups.google.com/forum/#!msg/rubyonrails-security/M4chq5Sb540/CC1Fh0Y_NWwJ
- https://groups.google.com/forum/message/raw?msg=rubyonrails-security/M4chq5Sb540/CC1Fh0Y_NWwJ
- http://openwall.com/lists/oss-security/2014/08/18/10
- http://rhn.redhat.com/errata/RHSA-2014-1102.html
