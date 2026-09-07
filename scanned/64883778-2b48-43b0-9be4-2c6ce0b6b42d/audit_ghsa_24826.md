# [H] RubyGems has Origin Validation Error vulnerability

## Summary
Severity: High
Advisory: GHSA-73w7-6w9g-gc8w
CVE: CVE-2017-0902
CWE: CWE-346, CWE-350
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-73w7-6w9g-gc8w
Type: github-advisory

## Affected
- RubyGems: `rubygems-update` — affected >=0 <2.6.13

## Details
RubyGems version 2.6.12 and earlier is vulnerable to a DNS hijacking vulnerability that allows a MITM attacker to force the RubyGems client to download and install gems from a server that the attacker controls.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-0902
- https://github.com/rubygems/rubygems/commit/8d91516fb7037ecfb27622f605dc40245e0f8d32
- https://hackerone.com/reports/218088
- https://access.redhat.com/errata/RHSA-2017:3485
- https://access.redhat.com/errata/RHSA-2018:0378
- https://access.redhat.com/errata/RHSA-2018:0583
- https://access.redhat.com/errata/RHSA-2018:0585
- https://github.com/rubygems/rubygems
- https://lists.debian.org/debian-lts-announce/2018/07/msg00012.html
- https://security.gentoo.org/glsa/201710-01
- https://usn.ubuntu.com/3553-1
- https://usn.ubuntu.com/3685-1
- https://web.archive.org/web/20170907040741/http://www.securityfocus.com/bid/100586
- https://web.archive.org/web/20170907215801/http://www.securitytracker.com/id/1039249
- https://www.debian.org/security/2017/dsa-3966
- http://blog.rubygems.org/2017/08/27/2.6.13-released.html
