# [H] fuse-uring: Avoid use-after-free in fuse_uring_async_stop_queues

## Summary
Severity: High
Advisory: CVE-2026-64261
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64261
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

fuse-uring: Avoid use-after-free in fuse_uring_async_stop_queues

fuse_uring_async_stop_queues() might run when the last reference
on ring->queue_refs was already dropped.

In order to avoid an early destruction a reference on struct fuse_conn
is now taken before starting fuse_uring_async_stop_queues() and that
reference is only released when that delayed work queue terminates.

## References
- https://git.kernel.org/stable/c/23a356e0bd96c8d5fb3ddff069f692bf10cab5c1
- https://git.kernel.org/stable/c/95d7f50aff2a5f71557263ff25b97b2951f32bf8
- https://git.kernel.org/stable/c/d351da75066955144515cb2f9aa959f24a04287a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64261.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64261
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
