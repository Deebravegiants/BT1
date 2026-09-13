# [H] net/sched: sch_qfq: Fix race condition on qfq_aggregate

## Summary
Severity: High
Advisory: CVE-2025-38477
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-28
Source: https://osv.dev/vulnerability/CVE-2025-38477
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.147, >=6.2.0 <6.6.100, >=6.7.0 <6.12.40, >=6.13.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: sch_qfq: Fix race condition on qfq_aggregate

A race condition can occur when 'agg' is modified in qfq_change_agg
(called during qfq_enqueue) while other threads access it
concurrently. For example, qfq_dump_class may trigger a NULL
dereference, and qfq_delete_class may cause a use-after-free.

This patch addresses the issue by:

1. Moved qfq_destroy_class into the critical section.

2. Added sch_tree_lock protection to qfq_dump_class and
qfq_dump_class_stats.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/466e10194ab81caa2ee6a332d33ba16bcceeeba6
- https://git.kernel.org/stable/c/5e28d5a3f774f118896aec17a3a20a9c5c9dfc64
- https://git.kernel.org/stable/c/a6d735100f602c830c16d69fb6d780eebd8c9ae1
- https://git.kernel.org/stable/c/aa7a22c4d678bf649fd3a1d27debec583563414d
- https://git.kernel.org/stable/c/c000a3a330d97f6c073ace5aa5faf94b9adb4b79
- https://git.kernel.org/stable/c/c6df794000147a3a02f79984aada4ce83f8d0a1e
- https://git.kernel.org/stable/c/d841aa5518508ab195b6781ad0d73ee378d713dd
- https://git.kernel.org/stable/c/fbe48f06e64134dfeafa89ad23387f66ebca3527
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38477.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38477
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
