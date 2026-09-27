# [H] RDMA/efa: Fix wrong resources deallocation order

## Summary
Severity: High
Advisory: CVE-2023-54201
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54201
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <6.1.53, >=6.2.0 <6.4.16, >=6.5.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/efa: Fix wrong resources deallocation order

When trying to destroy QP or CQ, we first decrease the refcount and
potentially free memory regions allocated for the object and then
request the device to destroy the object. If the device fails, the
object isn't fully destroyed so the user/IB core can try to destroy the
object again which will lead to underflow when trying to decrease an
already zeroed refcount.

Deallocate resources in reverse order of allocating them to safely free
them.

## References
- https://git.kernel.org/stable/c/24f9884971f9b34915b67baacf7350a3f6f19ea4
- https://git.kernel.org/stable/c/cf38960386f3cc4abf395e556af915e4babcafd2
- https://git.kernel.org/stable/c/dc202c57e9a1423aed528e4b8dc949509cd32191
- https://git.kernel.org/stable/c/e79db2f51a564fd4daa3e508b987df5e81c34b20
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54201.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54201
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
