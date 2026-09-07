# [H] actionpack allows remote code execution via application's unrestricted use of render method

## Summary
Severity: High
Advisory: GHSA-78rc-8c29-p45g
CVE: CVE-2016-2098
CWE: CWE-20
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-78rc-8c29-p45g
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=3.0.0 <3.2.22.2
- RubyGems: `actionpack` — affected >=4.0.0 <4.1.14.2
- RubyGems: `actionpack` — affected >=4.2.0 <4.2.5.2

## Details
Action Pack in Ruby on Rails before 3.2.22.2, 4.x before 4.1.14.2, and 4.2.x before 4.2.5.2 allows remote attackers to execute arbitrary Ruby code by leveraging an application's unrestricted use of the render method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2098
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2016-2098.yml
- https://groups.google.com/forum/#!topic/rubyonrails-security/ly-IH-fxr_Q
- https://web.archive.org/web/20200228015318/http://www.securityfocus.com/bid/83725
- https://web.archive.org/web/20210612214217/https://groups.google.com/forum/message/raw?msg=rubyonrails-security/ly-IH-fxr_Q/WLoOhcMZIAAJ
- https://web.archive.org/web/20211205173437/https://securitytracker.com/id/1035122
- https://www.exploit-db.com/exploits/40086
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00057.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00080.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00083.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00086.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00053.html
- http://weblog.rubyonrails.org/2016/2/29/Rails-4-2-5-2-4-1-14-2-3-2-22-2-have-been-released
- http://www.debian.org/security/2016/dsa-3509
