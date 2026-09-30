# [C] ntfs: grow index root value before reparent header update

## Summary
Severity: Critical
Advisory: CVE-2026-72211
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72211
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: grow index root value before reparent header update

ntfs_ir_reparent() moves the resident index root entries into an index
block and leaves a small root stub containing the child VCN. That root
stub can be larger than the existing resident value. For example, an
empty root with value_length 48 has an index area of 32 bytes, while the
large-index root stub needs index_length and allocated_size of 40 bytes.

The current code publishes the larger index.index_length and
index.allocated_size before resizing the resident value. If the resize
returns -ENOSPC, the recovery path can call ntfs_inode_add_attrlist(),
which looks attributes up again while the root header says
allocated_size 40 but the resident value still only provides 32 bytes of
index area. Lookup-time $INDEX_ROOT validation then correctly rejects
that transient layout as corrupt.

This reproduces as a generic/013 failure under qemu. In the failing run,
the transient root had value_len=48, index_size=32, index_length=40, and
allocated_size=40, and ntfsprogs-plus ntfsck reported "Corrupt index
root in MFT record 1177".

When the root stub grows, resize the resident value before publishing the
larger root header. If the resize fails, the old root remains valid for
recovery lookups. Keep the existing header-before-resize ordering for
shrink or same-size cases so the resident value never temporarily
exposes an allocated_size beyond its bounds.

## References
- https://git.kernel.org/stable/c/0bb508fb3b97e4802ec727fd2af4d608f65dd190
- https://git.kernel.org/stable/c/38d444271604afc6381ddb5a181e391915c35fae
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72211.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72211
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
