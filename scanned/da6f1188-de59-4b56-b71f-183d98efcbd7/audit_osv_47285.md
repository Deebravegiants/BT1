# [H] CVE-2016-2143

## Summary
Severity: High
Advisory: CVE-2016-2143
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-04-27
Source: https://osv.dev/vulnerability/CVE-2016-2143
Type: osv

## Details
The fork implementation in the Linux kernel before 4.5 on s390 platforms mishandles the case of four page-table levels, which allows local users to cause a denial of service (system crash) or possibly have unspecified other impact via a crafted application, related to arch/s390/include/asm/mmu_context.h and arch/s390/include/asm/pgalloc.h.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00019.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00052.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00059.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00038.html
- http://rhn.redhat.com/errata/RHSA-2016-2766.html
- http://www.debian.org/security/2016/dsa-3607
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00005.html
- http://rhn.redhat.com/errata/RHSA-2016-1539.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- https://security-tracker.debian.org/tracker/CVE-2016-2143
- https://github.com/torvalds/linux/commit/3446c13b268af86391d06611327006b059b8bab1
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=3446c13b268af86391d06611327006b059b8bab1
