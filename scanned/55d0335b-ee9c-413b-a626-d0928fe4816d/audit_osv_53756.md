# [M] CVE-2023-23454

## Summary
Severity: Medium
Advisory: CVE-2023-23454
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-12
Source: https://osv.dev/vulnerability/CVE-2023-23454
Type: osv

## Details
cbq_classify in net/sched/sch_cbq.c in the Linux kernel through 6.1.4 allows attackers to cause a denial of service (slab-out-of-bounds read) because of type confusion (non-negative numbers can sometimes indicate a TC_ACT_SHOT condition rather than valid classification results).

## References
- https://lists.debian.org/debian-lts-announce/2023/03/msg00000.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://www.debian.org/security/2023/dsa-5324
- https://www.openwall.com/lists/oss-security/2023/01/10/1
- https://www.openwall.com/lists/oss-security/2023/01/10/4
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=caa4b35b4317d5147b3ab0fbdc9c075c7d2e9c12
