# [H] RubyGems may allow a maliciously crafted gem to overwrite files

## Summary
Severity: High
Advisory: GHSA-pm9x-4392-2c2p
CVE: CVE-2017-0901
CWE: CWE-20, CWE-22
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-pm9x-4392-2c2p
Type: github-advisory

## Affected
- RubyGems: `rubygems-update` — affected >=0 <2.6.13

## Details
RubyGems versions 2.6.12 and earlier fail to validate specification names, allowing a maliciously crafted gem to potentially overwrite any file on the filesystem.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-0901
- https://github.com/rubygems/rubygems/commit/ad5c0a53a86ca5b218c7976765c0365b91d22cb2
- https://hackerone.com/reports/243156
- https://access.redhat.com/errata/RHSA-2017:3485
- https://access.redhat.com/errata/RHSA-2018:0378
- https://access.redhat.com/errata/RHSA-2018:0583
- https://access.redhat.com/errata/RHSA-2018:0585
- https://github.com/rubygems/rubygems
- https://lists.debian.org/debian-lts-announce/2018/07/msg00012.html
- https://security.gentoo.org/glsa/201710-01
- https://usn.ubuntu.com/3553-1
- https://usn.ubuntu.com/3685-1
- https://web.archive.org/web/20170907215801/http://www.securitytracker.com/id/1039249
- https://web.archive.org/web/20170915000000*/http://www.securityfocus.com/bid/100580#:~:text=1%20snapshot-,16%3A05%3A26,-Note
- https://www.debian.org/security/2017/dsa-3966
- https://www.exploit-db.com/exploits/42611
- http://blog.rubygems.org/2017/08/27/2.6.13-released.html
