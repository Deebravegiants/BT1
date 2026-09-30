# [H] CVE-2020-29370

## Summary
Severity: High
Advisory: CVE-2020-29370
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-28
Source: https://osv.dev/vulnerability/CVE-2020-29370
Type: osv

## Details
An issue was discovered in kmem_cache_alloc_bulk in mm/slub.c in the Linux kernel before 5.5.11. The slowpath lacks the required TID increment, aka CID-fd4d9c7d0c71.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.5.11
- https://security.netapp.com/advisory/ntap-20201218-0001/
- https://bugs.chromium.org/p/project-zero/issues/detail?id=2022
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=fd4d9c7d0c71866ec0c2825189ebd2ce35bd95b8
