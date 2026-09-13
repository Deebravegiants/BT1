# [H] WEBrick RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-369m-2gv6-mw28
CVE: CVE-2017-10784
CWE: CWE-287
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-369m-2gv6-mw28
Type: github-advisory

## Affected
- RubyGems: `webrick` — affected >=0 <1.4.0

## Details
The Basic authentication code in WEBrick library in Ruby before 2.2.8, 2.3.x before 2.3.5, and 2.4.x through 2.4.1 allows remote attackers to inject terminal emulator escape sequences into its log and possibly execute arbitrary commands via a crafted user name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-10784
- https://github.com/ruby/ruby/commit/6617c41292
- https://github.com/ruby/webrick/commit/4ac0f3843ab82d1c31e1cfc719409208adef7813
- https://hackerone.com/reports/223363
- https://www.ruby-lang.org/en/news/2017/09/14/webrick-basic-auth-escape-sequence-injection-cve-2017-10784
- https://www.ruby-lang.org/en/news/2017/09/14/ruby-2-3-5-released
- https://www.ruby-lang.org/en/news/2017/09/14/ruby-2-2-8-released
- https://www.debian.org/security/2017/dsa-4031
- https://web.archive.org/web/20211025092552/http://www.securitytracker.com/id/1039363
- https://web.archive.org/web/20210919031115/http://www.securitytracker.com/id/1042004
- https://web.archive.org/web/20210621131814/http://www.securityfocus.com/bid/100853
- https://usn.ubuntu.com/3685-1
- https://usn.ubuntu.com/3528-1
- https://security.gentoo.org/glsa/201710-18
- https://lists.debian.org/debian-lts-announce/2018/07/msg00012.html
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/webrick/CVE-2017-10784.yml
- https://github.com/ruby/webrick
- https://access.redhat.com/errata/RHSA-2018:0585
- https://access.redhat.com/errata/RHSA-2018:0583
- https://access.redhat.com/errata/RHSA-2018:0378
