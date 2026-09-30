# [M] CVE-2021-4002

## Summary
Severity: Medium
Advisory: CVE-2021-4002
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2022-03-03
Source: https://osv.dev/vulnerability/CVE-2021-4002
Type: osv

## Details
A memory leak flaw in the Linux kernel's hugetlbfs memory usage was found in the way the user maps some regions of memory twice using shmget() which are aligned to PUD alignment with the fault of some of the memory pages. A local user could use this flaw to get unauthorized access to some data.

## References
- https://lists.debian.org/debian-lts-announce/2022/03/msg00011.html
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
- https://www.debian.org/security/2022/dsa-5096
- https://bugzilla.redhat.com/show_bug.cgi?id=2025726
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=13e4ad2ce8df6e058ef482a31fdd81c725b0f7ea
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=a4a118f2eead1d6c49e00765de89878288d4b890
- https://www.openwall.com/lists/oss-security/2021/11/25/1
