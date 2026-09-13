# [M] CVE-2021-29264

## Summary
Severity: Medium
Advisory: CVE-2021-29264
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-26
Source: https://osv.dev/vulnerability/CVE-2021-29264
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.11.10. drivers/net/ethernet/freescale/gianfar.c in the Freescale Gianfar Ethernet driver allows attackers to cause a system crash because a negative fragment size is calculated in situations involving an rx queue overrun when jumbo packets are used and NAPI is enabled, aka CID-d8861bab48b6.

## References
- https://lists.debian.org/debian-lts-announce/2021/06/msg00019.html
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?id=d8861bab48b6c1fc3cdbcab8ff9d1eaea43afe7f
