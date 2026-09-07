# [H] ActiveRecord in Ruby on Rails allows database-query bypass

## Summary
Severity: High
Advisory: GHSA-pr3r-4wrp-r2pv
CVE: CVE-2016-6317
CWE: CWE-284, CWE-476
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-pr3r-4wrp-r2pv
Type: github-advisory

## Affected
- RubyGems: `activerecord` — affected >=4.2.0 <4.2.7.1

## Details
Active Record in Ruby on Rails 4.2.x before 4.2.7.1 does not properly consider differences in parameter handling between the Active Record component and the JSON implementation, which allows remote attackers to bypass intended database-query restrictions and perform NULL checks or trigger missing WHERE clauses via a crafted request, as demonstrated by certain "[nil]" values, a related issue to CVE-2012-2660, CVE-2012-2694, and CVE-2013-0155.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6317
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activerecord/CVE-2016-6317.yml
- https://groups.google.com/forum/#!topic/ruby-security-ann/WccgKSKiPZA
- https://groups.google.com/forum/#!topic/rubyonrails-security/rgO20zYW33s
- http://rhn.redhat.com/errata/RHSA-2016-1855.html
- http://weblog.rubyonrails.org/2016/8/11/Rails-5-0-0-1-4-2-7-2-and-3-2-22-3-have-been-released
- http://www.openwall.com/lists/oss-security/2016/08/11/4
