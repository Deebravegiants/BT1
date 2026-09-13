# [M] CVE-2023-0458

## Summary
Severity: Medium
Advisory: CVE-2023-0458
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-26
Source: https://osv.dev/vulnerability/CVE-2023-0458
Type: osv

## Details
A speculative pointer dereference problem exists in the Linux Kernel on the do_prlimit() function. The resource argument value is controlled and is used in pointer arithmetic for the 'rlim' variable and can be used to leak the contents. We recommend upgrading past version 6.1.8 or commit 739790605705ddcf18f21782b9c99ad7d53a8c11

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/diff/kernel/sys.c?id=v6.1.8&id2=v6.1.7
- https://github.com/torvalds/linux/commit/739790605705ddcf18f21782b9c99ad7d53a8c11
