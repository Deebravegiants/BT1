# [M] CVE-2020-29373

## Summary
Severity: Medium
Advisory: CVE-2020-29373
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2020-11-28
Source: https://osv.dev/vulnerability/CVE-2020-29373
Type: osv

## Details
An issue was discovered in fs/io_uring.c in the Linux kernel before 5.6. It unsafely handles the root directory during path lookups, and thus a process inside a mount namespace can escape to unintended filesystem locations, aka CID-ff002b30181d.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6
- https://bugs.chromium.org/p/project-zero/issues/detail?id=2011
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=ff002b30181d30cdfbca316dadd099c3ca0d739c
