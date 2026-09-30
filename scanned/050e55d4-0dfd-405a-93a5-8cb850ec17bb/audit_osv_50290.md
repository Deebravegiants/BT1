# [M] CVE-2020-11494

## Summary
Severity: Medium
Advisory: CVE-2020-11494
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-04-02
Source: https://osv.dev/vulnerability/CVE-2020-11494
Type: osv

## Details
An issue was discovered in slc_bump in drivers/net/can/slcan.c in the Linux kernel 3.16 through 5.6.2. It allows attackers to read uninitialized can_frame data, potentially containing sensitive information from kernel stack memory, if the configuration lacks CONFIG_INIT_STACK_ALL, aka CID-b9258a2cece4.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00035.html
- http://packetstormsecurity.com/files/159565/Kernel-Live-Patch-Security-Notice-LSN-0072-1.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- https://usn.ubuntu.com/4368-1/
- https://usn.ubuntu.com/4369-1/
- https://www.debian.org/security/2020/dsa-4698
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://security.netapp.com/advisory/ntap-20200430-0004/
- https://usn.ubuntu.com/4363-1/
- https://usn.ubuntu.com/4364-1/
- https://git.kernel.org/pub/scm/linux/kernel/git/tip/tip.git/commit/?id=08fadc32ce6239dc75fd5e869590e29bc62bbc28
- https://github.com/torvalds/linux/commit/b9258a2cece4ec1f020715fe3554bc2e360f6264
