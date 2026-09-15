# [M] CVE-2017-5969

## Summary
Severity: Medium
Advisory: CVE-2017-5969
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-11
Source: https://osv.dev/vulnerability/CVE-2017-5969
Type: osv

## Details
libxml2 2.9.4, when used in recover mode, allows remote attackers to cause a denial of service (NULL pointer dereference) via a crafted XML document.  NOTE: The maintainer states "I would disagree of a CVE with the Recover parsing option which should only be used for manual recovery at least for XML parser.

## References
- https://lists.debian.org/debian-lts-announce/2022/04/msg00004.html
- http://www.openwall.com/lists/oss-security/2016/11/05/3
- http://www.openwall.com/lists/oss-security/2017/02/13/1
- http://www.securityfocus.com/bid/96188
- https://security.gentoo.org/glsa/201711-01
- https://bugzilla.gnome.org/show_bug.cgi?id=778519
