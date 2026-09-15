# [M] ActiveRecord vulnerable to modification of protected model attributes

## Summary
Severity: Medium
Advisory: GHSA-gr44-7grc-37vq
CVE: CVE-2013-0276
CWE: CWE-284
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-gr44-7grc-37vq
Type: github-advisory

## Affected
- RubyGems: `activerecord` — affected >=0 <2.3.17
- RubyGems: `activerecord` — affected >=3.1.0 <3.1.11
- RubyGems: `activerecord` — affected >=3.2.0 <3.2.12

## Details
ActiveRecord in Ruby on Rails before 2.3.17, 3.1.x before 3.1.11, and 3.2.x before 3.2.12 allows remote attackers to bypass the `attr_protected` protection mechanism and modify protected model attributes via a crafted request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-0276
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activerecord/CVE-2013-0276.yml
- https://groups.google.com/group/rubyonrails-security/msg/bb44b98a73ef1a06?dmode=source&output=gplain
- https://web.archive.org/web/20130217055442/http://www.securityfocus.com/bid/57896
- http://lists.apple.com/archives/security-announce/2013/Jun/msg00000.html
- http://lists.opensuse.org/opensuse-updates/2013-03/msg00048.html
- http://rhn.redhat.com/errata/RHSA-2013-0686.html
- http://support.apple.com/kb/HT5784
- http://weblog.rubyonrails.org/2013/2/11/SEC-ANN-Rails-3-2-12-3-1-11-and-2-3-17-have-been-released
- http://www.debian.org/security/2013/dsa-2620
- http://www.openwall.com/lists/oss-security/2013/02/11/5
