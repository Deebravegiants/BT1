# [M] CVE-2018-1091

## Summary
Severity: Medium
Advisory: CVE-2018-1091
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-27
Source: https://osv.dev/vulnerability/CVE-2018-1091
Type: osv

## Details
In the flush_tmregs_to_thread function in arch/powerpc/kernel/ptrace.c in the Linux kernel before 4.13.5, a guest kernel crash can be triggered from unprivileged userspace during a core dump on a POWER host due to a missing processor feature check and an erroneous use of transactional memory (TM) instructions in the core dump path, leading to a denial of service.

## References
- http://openwall.com/lists/oss-security/2018/03/27/4
- https://access.redhat.com/errata/RHSA-2018:1318
- https://access.redhat.com/security/cve/cve-2018-1091
- https://bugzilla.redhat.com/show_bug.cgi?id=1558149
- https://marc.info/?l=linuxppc-embedded&m=150535531910494&w=2
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.5
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c1fa0768a8713b135848f78fd43ffc208d8ded70
- https://github.com/torvalds/linux/commit/c1fa0768a8713b135848f78fd43ffc208d8ded70
