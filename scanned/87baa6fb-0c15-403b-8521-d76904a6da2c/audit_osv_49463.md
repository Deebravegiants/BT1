# [H] CVE-2019-12817

## Summary
Severity: High
Advisory: CVE-2019-12817
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-25
Source: https://osv.dev/vulnerability/CVE-2019-12817
Type: osv

## Details
arch/powerpc/mm/mmu_context_book3s64.c in the Linux kernel before 5.1.15 for powerpc has a bug where unrelated processes may be able to read/write to one another's virtual memory under certain conditions via an mmap above 512 TB. Only a subset of powerpc systems are affected.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WSKLL2374YGFQR6LSVCFGTTCRGBTLAWZ/
- http://www.securityfocus.com/bid/108884
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OTLN3KQYEEWWAJYA4BUYYDMWWXCJQNV2/
- https://support.f5.com/csp/article/K12876166?utm_source=f5support&amp%3Butm_medium=RSS
- https://access.redhat.com/errata/RHSA-2019:2703
- https://seclists.org/bugtraq/2019/Aug/13
- https://support.f5.com/csp/article/K12876166
- https://usn.ubuntu.com/4031-1/
- https://www.debian.org/security/2019/dsa-4495
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00025.html
- http://www.openwall.com/lists/oss-security/2019/06/24/5
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.15
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=ca72d88378b2f2444d3ec145dd442d449d3fefbc
