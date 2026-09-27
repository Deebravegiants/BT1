# [H] CVE-2023-31436

## Summary
Severity: High
Advisory: CVE-2023-31436
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-28
Source: https://osv.dev/vulnerability/CVE-2023-31436
Type: osv

## Details
qfq_change_class in net/sched/sch_qfq.c in the Linux kernel before 6.2.13 allows an out-of-bounds write because lmax can exceed QFQ_MIN_LMAX.

## References
- http://packetstormsecurity.com/files/175963/Kernel-Live-Patch-Security-Notice-LSN-0099-1.html
- https://security.netapp.com/advisory/ntap-20230609-0001/
- http://packetstormsecurity.com/files/173087/Kernel-Live-Patch-Security-Notice-LSN-0095-1.html
- http://packetstormsecurity.com/files/173757/Kernel-Live-Patch-Security-Notice-LSN-0096-1.html
- https://lists.debian.org/debian-lts-announce/2023/06/msg00008.html
- https://www.debian.org/security/2023/dsa-5402
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.2.13
- https://github.com/torvalds/linux/commit/3037933448f60f9acb705997eae62013ecb81e0d
- https://www.spinics.net/lists/stable-commits/msg294885.html
