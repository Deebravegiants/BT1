# [H] actionpack Path Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-6x85-j5j2-27jx
CVE: CVE-2014-0130
CWE: CWE-22
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N/E:H (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-6x85-j5j2-27jx
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=3.0.0 <3.2.18
- RubyGems: `actionpack` — affected >=4.0.0 <4.0.5
- RubyGems: `actionpack` — affected >=4.1.0 <4.1.1

## Details
Directory traversal vulnerability in `actionpack/lib/abstract_controller/base.rb` in the implicit-render implementation in Ruby on Rails before 3.2.18, 4.0.x before 4.0.5, and 4.1.x before 4.1.1, when certain route globbing configurations are enabled, allows remote attackers to read arbitrary files via a crafted request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0130
- https://access.redhat.com/errata/RHSA-2014:0510
- https://access.redhat.com/errata/RHSA-2014:0816
- https://access.redhat.com/errata/RHSA-2014:1863
- https://access.redhat.com/security/cve/CVE-2014-0130
- https://bugzilla.redhat.com/show_bug.cgi?id=1095105
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2014-0130.yml
- https://groups.google.com/forum/#!topic/rubyonrails-security/NkKc7vTW70o
- https://groups.google.com/forum/message/raw?msg=rubyonrails-security/NkKc7vTW70o/NxW_PDBSG3AJ
- https://web.archive.org/web/20140518192004/http://www.securityfocus.com/bid/67244
- https://web.archive.org/web/20150319054505/http://matasano.com/research/AnatomyOfRailsVuln-CVE-2014-0130.pdf
- https://web.archive.org/web/20210411041816/https://groups.google.com/forum/message/raw?msg=rubyonrails-security/NkKc7vTW70o/NxW_PDBSG3AJ
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2014-0130
- http://matasano.com/research/AnatomyOfRailsVuln-CVE-2014-0130.pdf
- http://rhn.redhat.com/errata/RHSA-2014-1863.html
