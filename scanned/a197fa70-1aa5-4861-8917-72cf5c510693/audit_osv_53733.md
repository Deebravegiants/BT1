# [M] CVE-2023-21400

## Summary
Severity: Medium
Advisory: CVE-2023-21400
Aliases: A-264663832, PUB-A-264663832
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-13
Source: https://osv.dev/vulnerability/CVE-2023-21400
Type: osv

## Details
In multiple functions  of io_uring.c, there is a possible kernel memory corruption due to improper locking. This could lead to local escalation of privilege in the kernel with System execution privileges needed. User interaction is not needed for exploitation.

## References
- http://www.openwall.com/lists/oss-security/2023/07/14/2
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://security.netapp.com/advisory/ntap-20240119-0012/
- https://source.android.com/security/bulletin/pixel/2023-07-01
- https://www.debian.org/security/2023/dsa-5480
- http://packetstormsecurity.com/files/175072/Kernel-Live-Patch-Security-Notice-LSN-0098-1.html
- http://www.openwall.com/lists/oss-security/2023/07/19/7
- http://www.openwall.com/lists/oss-security/2023/07/25/7
- http://www.openwall.com/lists/oss-security/2023/07/19/2
