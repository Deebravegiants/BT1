# [C] CVE-2018-14600

## Summary
Severity: Critical
Advisory: CVE-2018-14600
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-24
Source: https://osv.dev/vulnerability/CVE-2018-14600
Type: osv

## Details
An issue was discovered in libX11 through 1.6.5. The function XListExtensions in ListExt.c interprets a variable as signed instead of unsigned, resulting in an out-of-bounds write (of up to 128 bytes), leading to DoS or remote code execution.

## References
- http://www.openwall.com/lists/oss-security/2018/08/21/6
- http://www.securityfocus.com/bid/105177
- http://www.securitytracker.com/id/1041543
- https://access.redhat.com/errata/RHSA-2019:2079
- https://lists.debian.org/debian-lts-announce/2018/08/msg00030.html
- https://lists.x.org/archives/xorg-announce/2018-August/002916.html
- https://security.gentoo.org/glsa/201811-01
- https://usn.ubuntu.com/3758-1/
- https://usn.ubuntu.com/3758-2/
- https://bugzilla.suse.com/show_bug.cgi?id=1102068
- https://cgit.freedesktop.org/xorg/lib/libX11/commit/?id=dbf72805fd9d7b1846fe9a11b46f3994bfc27fea
