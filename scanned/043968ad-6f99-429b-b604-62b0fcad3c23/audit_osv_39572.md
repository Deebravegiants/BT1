# [H] RDMA/mlx4: Fix mis-use of RCU in mlx4_srq_event()

## Summary
Severity: High
Advisory: CVE-2026-46181
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46181
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/mlx4: Fix mis-use of RCU in mlx4_srq_event()

Sashiko points out the radix_tree itself is RCU safe, but nothing ever
frees the mlx4_srq struct with RCU, and it isn't even accessed within the
RCU critical section. It also will crash if an event is delivered before
the srq object is finished initializing.

Use the spinlock since it isn't easy to make RCU work, use
refcount_inc_not_zero() to protect against partially initialized objects,
and order the refcount_set() to be after the srq is fully initialized.

## References
- https://git.kernel.org/stable/c/1e2a44875b6afb4add1115f7f3351dcbeb6f273d
- https://git.kernel.org/stable/c/8b7833f3bce35cb0d01c1503781523c099c675f0
- https://git.kernel.org/stable/c/c9341307ea16b9395c2e4c9c94d8499d91fe31d0
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46181.json
- https://access.redhat.com/errata/RHSA-2026:25120
- https://access.redhat.com/errata/RHSA-2026:25121
- https://access.redhat.com/errata/RHSA-2026:25217
- https://access.redhat.com/errata/RHSA-2026:33900
- https://access.redhat.com/errata/RHSA-2026:34094
- https://access.redhat.com/errata/RHSA-2026:34095
- https://access.redhat.com/errata/RHSA-2026:34443
- https://access.redhat.com/errata/RHSA-2026:35863
- https://access.redhat.com/errata/RHSA-2026:35894
- https://access.redhat.com/errata/RHSA-2026:35896
- https://access.redhat.com/errata/RHSA-2026:36216
- https://access.redhat.com/errata/RHSA-2026:41236
- https://access.redhat.com/security/cve/CVE-2026-46181
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46181.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46181
- https://bugzilla.redhat.com/show_bug.cgi?id=2482532
