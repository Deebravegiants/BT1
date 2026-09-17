# [H] CVE-2018-14598

## Summary
Severity: High
Advisory: CVE-2018-14598
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-24
Source: https://osv.dev/vulnerability/CVE-2018-14598
Type: osv

## Details
An issue was discovered in XListExtensions in ListExt.c in libX11 through 1.6.5. A malicious server can send a reply in which the first string overflows, causing a variable to be set to NULL that will be freed later on, leading to DoS (segmentation fault).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YGARUV66TS5OOSLR5A76BUB7SDV6GO4F/
- http://www.openwall.com/lists/oss-security/2018/08/21/6
- http://www.securityfocus.com/bid/105177
- http://www.securitytracker.com/id/1041543
- https://access.redhat.com/errata/RHSA-2019:2079
- https://lists.debian.org/debian-lts-announce/2018/08/msg00030.html
- https://lists.x.org/archives/xorg-announce/2018-August/002916.html
- https://security.gentoo.org/glsa/201811-01
- https://usn.ubuntu.com/3758-1/
- https://usn.ubuntu.com/3758-2/
- https://bugzilla.suse.com/show_bug.cgi?id=1102073
- https://cgit.freedesktop.org/xorg/lib/libX11/commit/?id=e83722768fd5c467ef61fa159e8c6278770b45c2
