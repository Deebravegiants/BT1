# [H] CVE-2023-28466

## Summary
Severity: High
Advisory: CVE-2023-28466
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-16
Source: https://osv.dev/vulnerability/CVE-2023-28466
Type: osv

## Details
do_tls_getsockopt in net/tls/tls_main.c in the Linux kernel through 6.2.6 lacks a lock_sock call, leading to a race condition (with a resultant use-after-free or NULL pointer dereference).

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://security.netapp.com/advisory/ntap-20230427-0006/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit?id=49c47cc21b5b7a3d8deb18fc57b0aa2ab1286962
