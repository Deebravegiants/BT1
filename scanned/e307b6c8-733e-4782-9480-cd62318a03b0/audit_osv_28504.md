# [H] f2fs: compress: don't allow unaligned truncation on released compress inode

## Summary
Severity: High
Advisory: CVE-2024-33847
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-06-24
Source: https://osv.dev/vulnerability/CVE-2024-33847
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: compress: don't allow unaligned truncation on released compress inode

f2fs image may be corrupted after below testcase:
- mkfs.f2fs -O extra_attr,compression -f /dev/vdb
- mount /dev/vdb /mnt/f2fs
- touch /mnt/f2fs/file
- f2fs_io setflags compression /mnt/f2fs/file
- dd if=/dev/zero of=/mnt/f2fs/file bs=4k count=4
- f2fs_io release_cblocks /mnt/f2fs/file
- truncate -s 8192 /mnt/f2fs/file
- umount /mnt/f2fs
- fsck.f2fs /dev/vdb

[ASSERT] (fsck_chk_inode_blk:1256)  --> ino: 0x5 has i_blocks: 0x00000002, but has 0x3 blocks
[FSCK] valid_block_count matching with CP             [Fail] [0x4, 0x5]
[FSCK] other corrupted bugs                           [Fail]

The reason is: partial truncation assume compressed inode has reserved
blocks, after partial truncation, valid block count may change w/o
.i_blocks and .total_valid_block_count update, result in corruption.

This patch only allow cluster size aligned truncation on released
compress inode for fixing.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/29ed2b5dd521ce7c5d8466cd70bf0cc9d07afeee
- https://git.kernel.org/stable/c/3ccf5210dc941a7aa0180596ac021568be4d35ec
- https://git.kernel.org/stable/c/5268241b41b1c5d0acca75e9b97d4fd719251c8c
- https://git.kernel.org/stable/c/8acae047215024d1ac499b3c8337ef1b952f160b
- https://git.kernel.org/stable/c/9f9341064a9b5246a32a7fe56b9f80c6f7f3c62d
- https://git.kernel.org/stable/c/b8962cf98595d1ec62f40f23667de830567ec8bc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/33xxx/CVE-2024-33847.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-33847
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
