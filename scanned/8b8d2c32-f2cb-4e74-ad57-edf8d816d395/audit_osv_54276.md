# [M] CVE-2023-45863

## Summary
Severity: Medium
Advisory: CVE-2023-45863
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-14
Source: https://osv.dev/vulnerability/CVE-2023-45863
Type: osv

## Details
An issue was discovered in lib/kobject.c in the Linux kernel before 6.2.3. With root access, an attacker can trigger a race condition that results in a fill_kobj_path out-of-bounds write.

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://lists.debian.org/debian-lts-announce/2024/01/msg00005.html
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.2.3
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=3bb2a01caa813d3a1845d378bbe4169ef280d394
