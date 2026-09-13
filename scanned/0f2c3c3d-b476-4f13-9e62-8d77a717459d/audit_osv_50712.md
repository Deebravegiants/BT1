# [H] CVE-2020-29569

## Summary
Severity: High
Advisory: CVE-2020-29569
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-29569
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.10.1, as used with Xen through 4.14.x. The Linux kernel PV block backend expects the kernel thread handler to reset ring->xenblkd to NULL when stopped. However, the handler may not have time to run if the frontend quickly toggles between the states connect and disconnect. As a consequence, the block backend may re-use a pointer after it was freed. A misbehaving guest can trigger a dom0 crash by continuously connecting / disconnecting a block frontend. Privilege escalation and information leaks cannot be ruled out. This only affects systems with a Linux blkback.

## References
- https://security.gentoo.org/glsa/202107-30
- https://security.netapp.com/advisory/ntap-20210205-0001/
- https://www.debian.org/security/2021/dsa-4843
- https://lists.debian.org/debian-lts-announce/2021/02/msg00018.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00010.html
- https://xenbits.xenproject.org/xsa/advisory-350.html
