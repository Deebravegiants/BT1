# [M] CVE-2020-29372

## Summary
Severity: Medium
Advisory: CVE-2020-29372
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-28
Source: https://osv.dev/vulnerability/CVE-2020-29372
Type: osv

## Details
An issue was discovered in do_madvise in mm/madvise.c in the Linux kernel before 5.6.8. There is a race condition between coredump operations and the IORING_OP_MADVISE implementation, aka CID-bc0c4d1e176e.

## References
- http://packetstormsecurity.com/files/162117/Kernel-Live-Patch-Security-Notice-LSN-0075-1.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.8
- https://bugs.chromium.org/p/project-zero/issues/detail?id=2029
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=bc0c4d1e176eeb614dc8734fc3ace34292771f11
