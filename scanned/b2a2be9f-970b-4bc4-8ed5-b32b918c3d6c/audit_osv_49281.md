# [H] CVE-2018-8822

## Summary
Severity: High
Advisory: CVE-2018-8822
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-20
Source: https://osv.dev/vulnerability/CVE-2018-8822
Type: osv

## Details
Incorrect buffer length handling in the ncp_read_kernel function in fs/ncpfs/ncplib_kernel.c in the Linux kernel through 4.15.11, and in drivers/staging/ncpfs/ncplib_kernel.c in the Linux kernel 4.16-rc through 4.16-rc6, could be exploited by malicious NCPFS servers to crash the kernel or execute code.

## References
- https://usn.ubuntu.com/3657-1/
- https://www.debian.org/security/2018/dsa-4187
- https://usn.ubuntu.com/3653-2/
- https://usn.ubuntu.com/3654-2/
- https://usn.ubuntu.com/3655-1/
- https://usn.ubuntu.com/3655-2/
- https://usn.ubuntu.com/3656-1/
- https://www.debian.org/security/2018/dsa-4188
- http://www.openwall.com/lists/oss-security/2022/12/27/3
- http://www.securityfocus.com/bid/103476
- https://lists.debian.org/debian-lts-announce/2018/05/msg00000.html
- https://usn.ubuntu.com/3653-1/
- https://usn.ubuntu.com/3654-1/
- https://www.mail-archive.com/netdev%40vger.kernel.org/msg223373.html
