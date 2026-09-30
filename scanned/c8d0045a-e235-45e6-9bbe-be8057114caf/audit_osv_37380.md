# [C] ext4: avoid infinite loops caused by residual data

## Summary
Severity: Critical
Advisory: CVE-2026-31448
Ecosystem: Linux
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31448
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <6.1.168, >=6.2.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: avoid infinite loops caused by residual data

On the mkdir/mknod path, when mapping logical blocks to physical blocks,
if inserting a new extent into the extent tree fails (in this example,
because the file system disabled the huge file feature when marking the
inode as dirty), ext4_ext_map_blocks() only calls ext4_free_blocks() to
reclaim the physical block without deleting the corresponding data in
the extent tree. This causes subsequent mkdir operations to reference
the previously reclaimed physical block number again, even though this
physical block is already being used by the xattr block. Therefore, a
situation arises where both the directory and xattr are using the same
buffer head block in memory simultaneously.

The above causes ext4_xattr_block_set() to enter an infinite loop about
"inserted" and cannot release the inode lock, ultimately leading to the
143s blocking problem mentioned in [1].

If the metadata is corrupted, then trying to remove some extent space
can do even more harm. Also in case EXT4_GET_BLOCKS_DELALLOC_RESERVE
was passed, remove space wrongly update quota information.
Jan Kara suggests distinguishing between two cases:

1) The error is ENOSPC or EDQUOT - in this case the filesystem is fully
consistent and we must maintain its consistency including all the
accounting. However these errors can happen only early before we've
inserted the extent into the extent tree. So current code works correctly
for this case.

2) Some other error - this means metadata is corrupted. We should strive to
do as few modifications as possible to limit damage. So I'd just skip
freeing of allocated blocks.

[1]
INFO: task syz.0.17:5995 blocked for more than 143 seconds.
Call Trace:
 inode_lock_nested include/linux/fs.h:1073 [inline]
 __start_dirop fs/namei.c:2923 [inline]
 start_dirop fs/namei.c:2934 [inline]

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/3a7667595bcad84da53fc156a418e110267c3412
- https://git.kernel.org/stable/c/416c86f30f91b4fb2642ef6b102596ca898f41a5
- https://git.kernel.org/stable/c/5422fe71d26d42af6c454ca9527faaad4e677d6c
- https://git.kernel.org/stable/c/64f425b06b3bea9abc8977fd3982779b3ad070c9
- https://git.kernel.org/stable/c/c66545e83a802c3851d9be27a41c0479dd29ff0c
- https://git.kernel.org/stable/c/ecc50bfca9b5c2ee6aeef998181689b80477367b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31448.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31448
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
