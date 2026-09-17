# [H] ocfs2: reserve space for inline xattr before attaching reflink tree

## Summary
Severity: High
Advisory: CVE-2024-49958
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49958
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.11.0 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: reserve space for inline xattr before attaching reflink tree

One of our customers reported a crash and a corrupted ocfs2 filesystem. 
The crash was due to the detection of corruption.  Upon troubleshooting,
the fsck -fn output showed the below corruption

[EXTENT_LIST_FREE] Extent list in owner 33080590 claims 230 as the next free chain record,
but fsck believes the largest valid value is 227.  Clamp the next record value? n

The stat output from the debugfs.ocfs2 showed the following corruption
where the "Next Free Rec:" had overshot the "Count:" in the root metadata
block.

        Inode: 33080590   Mode: 0640   Generation: 2619713622 (0x9c25a856)
        FS Generation: 904309833 (0x35e6ac49)
        CRC32: 00000000   ECC: 0000
        Type: Regular   Attr: 0x0   Flags: Valid
        Dynamic Features: (0x16) HasXattr InlineXattr Refcounted
        Extended Attributes Block: 0  Extended Attributes Inline Size: 256
        User: 0 (root)   Group: 0 (root)   Size: 281320357888
        Links: 1   Clusters: 141738
        ctime: 0x66911b56 0x316edcb8 -- Fri Jul 12 06:02:30.829349048 2024
        atime: 0x66911d6b 0x7f7a28d -- Fri Jul 12 06:11:23.133669517 2024
        mtime: 0x66911b56 0x12ed75d7 -- Fri Jul 12 06:02:30.317552087 2024
        dtime: 0x0 -- Wed Dec 31 17:00:00 1969
        Refcount Block: 2777346
        Last Extblk: 2886943   Orphan Slot: 0
        Sub Alloc Slot: 0   Sub Alloc Bit: 14
        Tree Depth: 1   Count: 227   Next Free Rec: 230
        ## Offset        Clusters       Block#
        0  0             2310           2776351
        1  2310          2139           2777375
        2  4449          1221           2778399
        3  5670          731            2779423
        4  6401          566            2780447
        .......          ....           .......
        .......          ....           .......

The issue was in the reflink workfow while reserving space for inline
xattr.  The problematic function is ocfs2_reflink_xattr_inline().  By the
time this function is called the reflink tree is already recreated at the
destination inode from the source inode.  At this point, this function
reserves space for inline xattrs at the destination inode without even
checking if there is space at the root metadata block.  It simply reduces
the l_count from 243 to 227 thereby making space of 256 bytes for inline
xattr whereas the inode already has extents beyond this index (in this
case up to 230), thereby causing corruption.

The fix for this is to reserve space for inline metadata at the destination
inode before the reflink tree gets recreated. The customer has verified the
fix.

## References
- https://git.kernel.org/stable/c/020f5c53c17f66c0a8f2d37dad27ace301b8d8a1
- https://git.kernel.org/stable/c/5c2072f02c0d75802ec28ec703b7d43a0dd008b5
- https://git.kernel.org/stable/c/5c9807c523b4fca81d3e8e864dabc8c806402121
- https://git.kernel.org/stable/c/5ca60b86f57a4d9648f68418a725b3a7de2816b0
- https://git.kernel.org/stable/c/637c00e06564a945e9d0edb3d78d362d64935f9f
- https://git.kernel.org/stable/c/74364cb578dcc0b6c9109519d19cbe5a56afac9a
- https://git.kernel.org/stable/c/96ce4c3537114d1698be635f5e36c62dc49df7a4
- https://git.kernel.org/stable/c/9f9a8f3ac65b4147f1a7b6c05fad5192c0e3c3d9
- https://git.kernel.org/stable/c/aac31d654a0a31cb0d2fa36ae694f4e164a52707
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49958.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49958
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
