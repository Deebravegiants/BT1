# [H] udf: validate free block extents against the partition length

## Summary
Severity: High
Advisory: CVE-2026-64324
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64324
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.11.0 <6.18.39, >=6.13.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

udf: validate free block extents against the partition length

udf_free_blocks() checks the logical block number and count against the
partition length, but drops the extent offset from that final bound.  A
crafted extent can pass the guard while logicalBlockNum + offset + count
points past the partition, which later indexes past the space bitmap
array.

A single ftruncate(2) on a file backed by such an extent reliably
panics the kernel.  This is a local availability issue.  On desktop
systems where UDisks/polkit allows the active user to mount removable
UDF media without CAP_SYS_ADMIN, an unprivileged local user can supply
the crafted filesystem and trigger the panic by truncating a writable
file on it.  Systems that require root or CAP_SYS_ADMIN to mount the
image have a higher prerequisite.

No confidentiality or integrity impact is claimed: the reproduced
primitive is an out-of-bounds read of a bitmap pointer slot followed by
a kernel panic.

Use the already computed logicalBlockNum + offset + count value for the
partition length check.  Also make load_block_bitmap() reject an
out-of-range block group before indexing s_block_bitmap[], so corrupted
callers cannot walk past the flexible array.

## References
- https://git.kernel.org/stable/c/12af328d2ee8d68e81ba612246d0b54b22d23e1f
- https://git.kernel.org/stable/c/335202ab25b01fdd45889ff25eab70864686dea3
- https://git.kernel.org/stable/c/5f0419457f89dce1a3f1c8e62a3adf2f39ab8168
- https://git.kernel.org/stable/c/9442d75429b0c556292a7454fe888d54259f5240
- https://git.kernel.org/stable/c/b54aee5652fcd7c23a0904a4623ec462c3edc70c
- https://git.kernel.org/stable/c/be87de7789a82a030a4896bc7683415ec9fa6f2b
- https://git.kernel.org/stable/c/fb49099206c5c57af28a157249fa7bcb5518f99e
- https://git.kernel.org/stable/c/fdd6229d2ae9914c1f25d1041db0f4f312a4fa76
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64324.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64324
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
