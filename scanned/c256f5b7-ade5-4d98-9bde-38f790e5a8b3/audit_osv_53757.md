# [M] CVE-2023-23455

## Summary
Severity: Medium
Advisory: CVE-2023-23455
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-12
Source: https://osv.dev/vulnerability/CVE-2023-23455
Type: osv

## Details
atm_tc_enqueue in net/sched/sch_atm.c in the Linux kernel through 6.1.4 allows attackers to cause a denial of service because of type confusion (non-negative numbers can sometimes indicate a TC_ACT_SHOT condition rather than valid classification results).

## References
- https://lists.debian.org/debian-lts-announce/2023/03/msg00000.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://www.debian.org/security/2023/dsa-5324
- https://www.openwall.com/lists/oss-security/2023/01/10/1
- https://www.openwall.com/lists/oss-security/2023/01/10/4
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=a2965c7be0522eaa18808684b7b82b248515511b
