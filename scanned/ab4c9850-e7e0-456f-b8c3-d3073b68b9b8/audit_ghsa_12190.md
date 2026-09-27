# [M] Active Record allows bypassing of database-query restrictions

## Summary
Severity: Medium
Advisory: GHSA-gppp-5xc5-wfpx
CVE: CVE-2013-0155
CWE: CWE-284
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-gppp-5xc5-wfpx
Type: github-advisory

## Affected
- RubyGems: `activerecord` — affected >=3.0.0 <3.0.19
- RubyGems: `activerecord` — affected >=3.1.0 <3.1.10
- RubyGems: `activerecord` — affected >=3.2.0 <3.2.11

## Details
Ruby on Rails 3.0.x before 3.0.19, 3.1.x before 3.1.10, and 3.2.x before 3.2.11 does not properly consider differences in parameter handling between the Active Record component and the JSON implementation, which allows remote attackers to bypass intended database-query restrictions and perform NULL checks or trigger missing WHERE clauses via a crafted request, as demonstrated by certain "[nil]" values, a related issue to CVE-2012-2660 and CVE-2012-2694.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-0155
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activerecord/CVE-2013-0155.yml
- https://groups.google.com/group/rubyonrails-security/msg/bc6f13dafe130ee9?dmode=source&output=gplain
- http://ics-cert.us-cert.gov/advisories/ICSA-13-036-01A
- http://lists.apple.com/archives/security-announce/2013/Jun/msg00000.html
- http://lists.opensuse.org/opensuse-updates/2013-12/msg00079.html
- http://lists.opensuse.org/opensuse-updates/2013-12/msg00081.html
- http://lists.opensuse.org/opensuse-updates/2013-12/msg00082.html
- http://lists.opensuse.org/opensuse-updates/2014-01/msg00003.html
- http://rhn.redhat.com/errata/RHSA-2013-0154.html
- http://support.apple.com/kb/HT5784
- http://www.debian.org/security/2013/dsa-2609
