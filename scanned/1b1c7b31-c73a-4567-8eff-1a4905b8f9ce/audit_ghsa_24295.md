# [C] RubyGems Code Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-7gcp-2gmq-w3xh
CVE: CVE-2017-0899
CWE: CWE-150, CWE-94
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-7gcp-2gmq-w3xh
Type: github-advisory

## Affected
- RubyGems: `rubygems-update` — affected >=0 <2.6.13

## Details
RubyGems prior to 2.6.13 is vulnerable to maliciously crafted gem specifications that include terminal escape characters. Printing the gem specification would execute terminal escape sequences.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-0899
- https://github.com/rubygems/rubygems/commit/1bcbc7fe637b03145401ec9c094066285934a7f1
- https://github.com/rubygems/rubygems/commit/ef0aa611effb5f54d40c7fba6e8235eb43c5a491
- https://hackerone.com/reports/226335
- https://access.redhat.com/errata/RHSA-2017:3485
- https://access.redhat.com/errata/RHSA-2018:0378
- https://access.redhat.com/errata/RHSA-2018:0583
- https://access.redhat.com/errata/RHSA-2018:0585
- https://github.com/rubygems/rubygems
- https://lists.debian.org/debian-lts-announce/2018/07/msg00012.html
- https://security.gentoo.org/glsa/201710-01
- https://web.archive.org/web/20170907215801/http://www.securitytracker.com/id/1039249
- https://web.archive.org/web/20170915000000*/http://www.securityfocus.com/bid/100576#:~:text=1%20snapshot-,11%3A49%3A33,-Note
- https://www.debian.org/security/2017/dsa-3966
- http://blog.rubygems.org/2017/08/27/2.6.13-released.html
