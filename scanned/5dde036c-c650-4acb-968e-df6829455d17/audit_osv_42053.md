# [H] Bluetooth: fix UAF in bt_accept_dequeue()

## Summary
Severity: High
Advisory: CVE-2026-64406
Ecosystem: Linux
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64406
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: fix UAF in bt_accept_dequeue()

bt_accept_get() takes a temporary reference before dropping the accept
queue lock. bt_accept_dequeue() currently drops that reference before
bt_accept_unlink(), leaving only the queue reference.

bt_accept_unlink() drops the queue reference. The subsequent
sock_hold() therefore accesses freed memory if it was the final
reference, as observed by KASAN during listening L2CAP socket cleanup.

Retain the temporary queue-walk reference through unlink and hand it to
the caller on success. Drop it explicitly on the closed and
not-yet-connected paths.

## References
- https://git.kernel.org/stable/c/0a98ff4e7b867f72fbb4e1237d81e9fa02ded0a0
- https://git.kernel.org/stable/c/26168db1ce5a9766cde021b18e590a101c056614
- https://git.kernel.org/stable/c/4bd0b274054f2679f28b70222b607bb0afc3ab9a
- https://git.kernel.org/stable/c/50c662bdcd51b03033a0abed6716bfd377ba1049
- https://git.kernel.org/stable/c/6303ed4bbe0095f4cc195225479bf506e010d1db
- https://git.kernel.org/stable/c/96ad400d5132eb333f28f6f1e2d58f0728ca9547
- https://git.kernel.org/stable/c/c0577c55219be42b6ea2ea8db11e85bfab6f4e8d
- https://git.kernel.org/stable/c/c66a95e60b65d876a927123b0ed36bd6177d9ca6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64406.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64406
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
