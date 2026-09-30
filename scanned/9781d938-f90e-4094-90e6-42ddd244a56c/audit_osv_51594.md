# [M] CVE-2021-34693

## Summary
Severity: Medium
Advisory: CVE-2021-34693
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-06-14
Source: https://osv.dev/vulnerability/CVE-2021-34693
Type: osv

## Details
net/can/bcm.c in the Linux kernel through 5.12.10 allows local users to obtain sensitive information from kernel stack memory because parts of a data structure are uninitialized.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=5e87ddbe3942e27e939bdc02deb8579b0cbd8ecc
- https://lore.kernel.org/netdev/trinity-87eaea25-2a7d-4aa9-92a5-269b822e5d95-1623609211076%403c-app-gmx-bs04/T/
- https://lists.debian.org/debian-lts-announce/2021/07/msg00014.html
- https://lists.debian.org/debian-lts-announce/2021/07/msg00015.html
- https://lists.debian.org/debian-lts-announce/2021/07/msg00016.html
- https://www.debian.org/security/2021/dsa-4941
- http://www.openwall.com/lists/oss-security/2021/06/15/1
