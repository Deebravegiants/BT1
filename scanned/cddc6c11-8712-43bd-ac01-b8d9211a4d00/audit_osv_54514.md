# [H] CVE-2024-0582

## Summary
Severity: High
Advisory: CVE-2024-0582
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-16
Source: https://osv.dev/vulnerability/CVE-2024-0582
Type: osv

## Details
A memory leak flaw was found in the Linux kernel’s io_uring functionality in how a user registers a buffer ring with IORING_REGISTER_PBUF_RING, mmap() it, and then frees it. This flaw allows a local user to crash or potentially escalate their privileges on the system.

## References
- http://www.openwall.com/lists/oss-security/2024/04/24/3
- https://access.redhat.com/security/cve/CVE-2024-0582
- https://bugs.chromium.org/p/project-zero/issues/detail?id=2504
- https://bugzilla.redhat.com/show_bug.cgi?id=2254050
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=c392cbecd8eca4c53f2bf508731257d9d0a21c2d
