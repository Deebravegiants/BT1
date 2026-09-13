# [H] RDMA/rxe: Fix double free in rxe_srq_from_init

## Summary
Severity: High
Advisory: CVE-2026-45852
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45852
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rxe: Fix double free in rxe_srq_from_init

In rxe_srq_from_init(), the queue pointer 'q' is assigned to
'srq->rq.queue' before copying the SRQ number to user space.
If copy_to_user() fails, the function calls rxe_queue_cleanup()
to free the queue, but leaves the now-invalid pointer in
'srq->rq.queue'.

The caller of rxe_srq_from_init() (rxe_create_srq) eventually
calls rxe_srq_cleanup() upon receiving the error, which triggers
a second rxe_queue_cleanup() on the same memory, leading to a
double free.

The call trace looks like this:
   kmem_cache_free+0x.../0x...
   rxe_queue_cleanup+0x1a/0x30 [rdma_rxe]
   rxe_srq_cleanup+0x42/0x60 [rdma_rxe]
   rxe_elem_release+0x31/0x70 [rdma_rxe]
   rxe_create_srq+0x12b/0x1a0 [rdma_rxe]
   ib_create_srq_user+0x9a/0x150 [ib_core]

Fix this by moving 'srq->rq.queue = q' after copy_to_user.

## References
- https://git.kernel.org/stable/c/0beefd0e15d962f497aad750b2d5e9c3570b66d1
- https://git.kernel.org/stable/c/26793db60925df1e88a29466813d586cbc190b8c
- https://git.kernel.org/stable/c/26a9cfe12f4ffdeaa136f252478986fa5f397ddc
- https://git.kernel.org/stable/c/5c07aef09a121a4cd622a71eb0753a9e135c84a8
- https://git.kernel.org/stable/c/9abff51163aa1bc275ec356f74fe976291860a7f
- https://git.kernel.org/stable/c/b98ab5494dbd48652561aa0b9c32f10500220745
- https://git.kernel.org/stable/c/ce6f8e007682f378279d4cf83b240f12d52c723b
- https://git.kernel.org/stable/c/d493e0bfc748a520c349d6c8791b262aa5ad2e4e
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-45852.json
- https://access.redhat.com/errata/RHSA-2026:25120
- https://access.redhat.com/errata/RHSA-2026:25121
- https://access.redhat.com/errata/RHSA-2026:25217
- https://access.redhat.com/errata/RHSA-2026:27713
- https://access.redhat.com/errata/RHSA-2026:33899
- https://access.redhat.com/errata/RHSA-2026:34094
- https://access.redhat.com/errata/RHSA-2026:35844
- https://access.redhat.com/errata/RHSA-2026:35863
- https://access.redhat.com/errata/RHSA-2026:35896
- https://access.redhat.com/errata/RHSA-2026:41236
- https://access.redhat.com/security/cve/CVE-2026-45852
