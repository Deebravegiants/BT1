# [C] CVE-2018-14599

## Summary
Severity: Critical
Advisory: CVE-2018-14599
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-24
Source: https://osv.dev/vulnerability/CVE-2018-14599
Type: osv

## Details
An issue was discovered in libX11 through 1.6.5. The function XListExtensions in ListExt.c is vulnerable to an off-by-one error caused by malicious server responses, leading to DoS or possibly unspecified other impact.

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
- https://bugzilla.suse.com/show_bug.cgi?id=1102062
- https://cgit.freedesktop.org/xorg/lib/libX11/commit/?id=b469da1430cdcee06e31c6251b83aede072a1ff0
