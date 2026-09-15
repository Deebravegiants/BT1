# [H] net/rds: Fix circular locking dependency in rds_tcp_tune

## Summary
Severity: High
Advisory: CVE-2026-23419
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-23419
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.6.130, >=6.7.0 <6.12.77, >=6.13.0 <6.18.17, >=6.19.0 <6.19.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/rds: Fix circular locking dependency in rds_tcp_tune

syzbot reported a circular locking dependency in rds_tcp_tune() where
sk_net_refcnt_upgrade() is called while holding the socket lock:

======================================================
WARNING: possible circular locking dependency detected
======================================================
kworker/u10:8/15040 is trying to acquire lock:
ffffffff8e9aaf80 (fs_reclaim){+.+.}-{0:0},
at: __kmalloc_cache_noprof+0x4b/0x6f0

but task is already holding lock:
ffff88805a3c1ce0 (k-sk_lock-AF_INET6){+.+.}-{0:0},
at: rds_tcp_tune+0xd7/0x930

The issue occurs because sk_net_refcnt_upgrade() performs memory
allocation (via get_net_track() -> ref_tracker_alloc()) while the
socket lock is held, creating a circular dependency with fs_reclaim.

Fix this by moving sk_net_refcnt_upgrade() outside the socket lock
critical section. This is safe because the fields modified by the
sk_net_refcnt_upgrade() call (sk_net_refcnt, ns_tracker) are not
accessed by any concurrent code path at this point.

v2:
  - Corrected fixes tag
  - check patch line wrap nits
  - ai commentary nits

## References
- https://git.kernel.org/stable/c/026bbaeeab9e04534ee58882b6447300629b42f6
- https://git.kernel.org/stable/c/6a877ececd6daa002a9a0002cd0fbca6592a9244
- https://git.kernel.org/stable/c/6ce948fa54599f369ff7fe8b793a6aae4b0762b2
- https://git.kernel.org/stable/c/8519e6883a942e510f33a0e634e27bcc3a844a40
- https://git.kernel.org/stable/c/8babb271403378ba6836f6c8599c5313d0e2355d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23419.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23419
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
