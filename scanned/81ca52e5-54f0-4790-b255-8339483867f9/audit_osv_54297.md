# [M] CVE-2023-46862

## Summary
Severity: Medium
Advisory: CVE-2023-46862
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-10-29
Source: https://osv.dev/vulnerability/CVE-2023-46862
Type: osv

## Details
An issue was discovered in the Linux kernel through 6.5.9. During a race with SQ thread exit, an io_uring/fdinfo.c io_uring_show_fdinfo NULL pointer dereference can occur.

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00005.html
- https://bugzilla.kernel.org/show_bug.cgi?id=218032#c4
- https://github.com/torvalds/linux/commit/7644b1a1c9a7ae8ab99175989bfc8676055edb46
