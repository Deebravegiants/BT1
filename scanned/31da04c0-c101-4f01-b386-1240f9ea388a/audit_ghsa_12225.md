# [M] activemodel contains Improper Input Validation

## Summary
Severity: Medium
Advisory: GHSA-543v-gj2c-r3ch
CVE: CVE-2016-0753
CWE: CWE-20
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-543v-gj2c-r3ch
Type: github-advisory

## Affected
- RubyGems: `activemodel` — affected >=4.1.0 <4.1.14.1
- RubyGems: `activemodel` — affected >=4.2.0 <4.2.5.1

## Details
Active Model in Ruby on Rails 4.1.x before 4.1.14.1, 4.2.x before 4.2.5.1, and 5.x before 5.0.0.beta1.1 supports the use of instance-level writers for class accessors, which allows remote attackers to bypass intended validation steps via crafted parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0753
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activemodel/CVE-2016-0753.yml
- https://groups.google.com/forum/#!topic/rubyonrails-security/6jQVC1geukQ
- https://web.archive.org/web/20160405205300/http://www.securitytracker.com/id/1034816
- https://web.archive.org/web/20200228000230/http://www.securityfocus.com/bid/82247
- https://web.archive.org/web/20210613054843/https://groups.google.com/forum/message/raw?msg=ruby-security-ann/6jQVC1geukQ/3Iy0GU1ZEgAJ
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/178041.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/178043.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/178047.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/178065.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/178066.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00053.html
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00043.html
- http://rhn.redhat.com/errata/RHSA-2016-0296.html
- http://www.debian.org/security/2016/dsa-3464
- http://www.openwall.com/lists/oss-security/2016/01/25/14
