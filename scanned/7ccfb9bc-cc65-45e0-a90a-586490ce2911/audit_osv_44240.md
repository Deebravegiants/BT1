# [H] hfsplus: Add a sanity check for btree node size

## Summary
Severity: High
Advisory: CVE-2026-80656
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80656
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

hfsplus: Add a sanity check for btree node size

Syzbot reported an uninit-value bug in [1] with a corrupted HFS+ image,
during the file system mounting process, specifically while loading the
catalog, a corrupted node_size value of 1 caused the rec_off argument
passed to hfs_bnode_read_u16() (within hfs_bnode_find()) to be excessively
large. Consequently, the function failed to return a valid value to
initialize the off variable, triggering the bug [1].

Every node starts from BTree node descriptor: struct hfs_bnode_desc.
So, the size of node cannot be lesser than that. However, technical
specification declares that: "The node size (which is expressed in bytes)
must be power of two, from 512 through 32,768, inclusive." Add a check
for btree node size base on technical specification.

[1]
BUG: KMSAN: uninit-value in hfsplus_bnode_find+0x141c/0x1600 fs/hfsplus/bnode.c:584
 hfsplus_bnode_find+0x141c/0x1600 fs/hfsplus/bnode.c:584
 hfsplus_btree_open+0x169a/0x1e40 fs/hfsplus/btree.c:382
 hfsplus_fill_super+0x111f/0x2770 fs/hfsplus/super.c:553
 get_tree_bdev_flags+0x6e6/0x920 fs/super.c:1694
 get_tree_bdev+0x38/0x50 fs/super.c:1717
 hfsplus_get_tree+0x35/0x40 fs/hfsplus/super.c:709
 vfs_get_tree+0xb3/0x5d0 fs/super.c:1754
 fc_mount fs/namespace.c:1193 [inline]

## References
- https://git.kernel.org/stable/c/306265eb9384d2c224f1b14d83a29323f0eab6d1
- https://git.kernel.org/stable/c/3f95e2661574ff13f099dd13456751933c280628
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80656.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80656
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
