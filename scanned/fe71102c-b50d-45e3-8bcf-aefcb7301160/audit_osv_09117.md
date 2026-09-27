# [C] CVE-2016-7993

## Summary
Severity: Critical
Advisory: CVE-2016-7993
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-28
Source: https://osv.dev/vulnerability/CVE-2016-7993
Type: osv

## Details
A bug in util-print.c:relts_print() in tcpdump before 4.9.0 could cause a buffer overflow in multiple protocol parsers (DNS, DVMRP, HSRP, IGMP, lightweight resolver protocol, PIM).

## References
- http://www.securitytracker.com/id/1037755
- https://www.mail-archive.com/debian-bugs-dist%40lists.debian.org/msg1494526.html
- http://www.debian.org/security/2017/dsa-3775
- http://www.securityfocus.com/bid/95852
- https://access.redhat.com/errata/RHSA-2017:1871
- https://security.gentoo.org/glsa/201702-30
