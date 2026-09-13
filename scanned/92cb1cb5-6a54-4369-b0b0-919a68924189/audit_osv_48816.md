# [H] CVE-2018-14622

## Summary
Severity: High
Advisory: CVE-2018-14622
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-30
Source: https://osv.dev/vulnerability/CVE-2018-14622
Type: osv

## Details
A null-pointer dereference vulnerability was found in libtirpc before version 0.3.3-rc3. The return value of makefd_xprt() was not checked in all instances, which could lead to a crash when the server exhausted the maximum number of available file descriptors. A remote attacker could cause an rpc-based application to crash by flooding it with new connections.

## References
- http://git.linux-nfs.org/?p=steved/libtirpc.git%3Ba=commit%3Bh=1c77f7a869bdea2a34799d774460d1f9983d45f0
- https://access.redhat.com/errata/RHBA-2017:1991
- https://lists.debian.org/debian-lts-announce/2018/08/msg00034.html
- https://usn.ubuntu.com/3759-1/
- https://usn.ubuntu.com/3759-2/
- https://bugzilla.novell.com/show_bug.cgi?id=968175
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14622
