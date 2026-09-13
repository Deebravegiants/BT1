# [M] CVE-2020-14344

## Summary
Severity: Medium
Advisory: CVE-2020-14344
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-08-05
Source: https://osv.dev/vulnerability/CVE-2020-14344
Type: osv

## Details
An integer overflow leading to a heap-buffer overflow was found in The X Input Method (XIM) client was implemented in libX11 before version 1.6.10. As per upstream this is security relevant when setuid programs call XIM client functions while running with elevated privileges. No such programs are shipped with Red Hat Enterprise Linux.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4VDDSAYV7XGNRCXE7HCU23645MG74OFF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7AVXCQOSCAPKYYHFIJAZ6E2C7LJBTLXF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XY4H2SIEF2362AMNX5ZKWAELGU7LKFJB/
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00014.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00024.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00031.html
- https://security.gentoo.org/glsa/202008-18
- https://usn.ubuntu.com/4487-1/
- https://usn.ubuntu.com/4487-2/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-14344
- https://lists.x.org/archives/xorg-announce/2020-July/003050.html
- https://www.openwall.com/lists/oss-security/2020/07/31/1
