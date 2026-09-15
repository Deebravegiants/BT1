# [M] CVE-2021-44879

## Summary
Severity: Medium
Advisory: CVE-2021-44879
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-02-14
Source: https://osv.dev/vulnerability/CVE-2021-44879
Type: osv

## Details
In gc_data_segment in fs/f2fs/gc.c in the Linux kernel before 5.16.3, special files are not considered, leading to a move_data_page NULL pointer dereference.

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://lists.debian.org/debian-lts-announce/2024/01/msg00005.html
- https://lore.kernel.org/linux-f2fs-devel/20211206144421.3735-3-chao%40kernel.org/T/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.3
- https://bugzilla.kernel.org/show_bug.cgi?id=215231
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=9056d6489f5a41cfbb67f719d2c0ce61ead72d9f
