# [H] CVE-2023-51782

## Summary
Severity: High
Advisory: CVE-2023-51782
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-11
Source: https://osv.dev/vulnerability/CVE-2023-51782
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.6.8. rose_ioctl in net/rose/af_rose.c has a use-after-free because of a rose_accept race condition.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.8
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://lists.debian.org/debian-lts-announce/2024/01/msg00005.html
- https://github.com/torvalds/linux/commit/810c38a369a0a0ce625b5c12169abce1dd9ccd53
