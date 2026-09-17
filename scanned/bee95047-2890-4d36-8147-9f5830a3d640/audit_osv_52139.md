# [M] CVE-2021-47116

## Summary
Severity: Medium
Advisory: CVE-2021-47116
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-15
Source: https://osv.dev/vulnerability/CVE-2021-47116
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix memory leak in ext4_mb_init_backend on error path.

Fix a memory leak discovered by syzbot when a file system is corrupted
with an illegally large s_log_groups_per_flex.

## References
- https://git.kernel.org/stable/c/04fb2baa0b147f51db065a1b13a11954abe592d0
- https://git.kernel.org/stable/c/2050c6e5b161e5e25ce3c420fef58b24fa388a49
- https://git.kernel.org/stable/c/a8867f4e3809050571c98de7a2d465aff5e4daf5
