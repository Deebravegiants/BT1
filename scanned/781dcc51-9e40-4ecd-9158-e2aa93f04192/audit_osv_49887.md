# [M] CVE-2019-20934

## Summary
Severity: Medium
Advisory: CVE-2019-20934
CVSS: 5.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2020-11-28
Source: https://osv.dev/vulnerability/CVE-2019-20934
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.2.6. On NUMA systems, the Linux fair scheduler has a use-after-free in show_numa_stats() because NUMA fault statistics are inappropriately freed, aka CID-16d51a590a8c.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.6
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1913
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=16d51a590a8ce3befb1308e0e7ab77f3b661af33
