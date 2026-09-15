# [H] Directory traversal vulnerability in Action View in Ruby on Rails

## Summary
Severity: High
Advisory: GHSA-xrr4-p6fq-hjg7
CVE: CVE-2016-0752
CWE: CWE-22
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N/E:H (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-xrr4-p6fq-hjg7
Type: github-advisory

## Affected
- RubyGems: `actionview` — affected >=4.0.0 <4.1.14.1
- RubyGems: `actionview` — affected >=4.2.0 <4.2.5.1
- RubyGems: `actionpack` — affected >=4.0.0 <4.1.14.1
- RubyGems: `actionpack` — affected >=4.2.0 <4.2.5.1
- RubyGems: `actionpack` — affected >=0 <3.2.22.1

## Details
Directory traversal vulnerability in Action View in Ruby on Rails before 3.2.22.1, 4.0.x and 4.1.x before 4.1.14.1, 4.2.x before 4.2.5.1, and 5.x before 5.0.0.beta1.1 allows remote attackers to read arbitrary files by leveraging an application's unrestricted use of the render method and providing a `..` (dot dot) in a pathname.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0752
- https://github.com/advisories/GHSA-xrr4-p6fq-hjg7
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2016-0752.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionview/CVE-2016-0752.yml
- https://groups.google.com/forum/#!topic/rubyonrails-security/335P1DcLG00
- https://groups.google.com/forum/message/raw?msg=ruby-security-ann/335P1DcLG00/JXcBnTtZEgAJ
- https://web.archive.org/web/20210618005620/https://groups.google.com/forum/message/raw?msg=ruby-security-ann/335P1DcLG00/JXcBnTtZEgAJ
- https://web.archive.org/web/20210621170450/http://www.securityfocus.com/bid/81801
- https://web.archive.org/web/20210723192420/http://www.securitytracker.com/id/1034816
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2016-0752
- https://www.exploit-db.com/exploits/40561
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/178044.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/178069.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00053.html
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00034.html
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00043.html
- http://rhn.redhat.com/errata/RHSA-2016-0296.html
- http://www.debian.org/security/2016/dsa-3464
- http://www.openwall.com/lists/oss-security/2016/01/25/13
- http://www.securityfocus.com/bid/81801
