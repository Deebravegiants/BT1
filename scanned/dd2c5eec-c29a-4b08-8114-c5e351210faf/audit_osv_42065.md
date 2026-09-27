# [H] ntfs: avoid calling post_write_mst_fixup() for invalid index_block

## Summary
Severity: High
Advisory: CVE-2026-64431
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64431
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: avoid calling post_write_mst_fixup() for invalid index_block

ntfs_icx_ib_sync_write() calls post_write_mst_fixup() when ntfs_ib_write()
returns an error, intending to restore the buffer after a failed write.

However, ntfs_ib_write() returns an error immediately if
pre_write_mst_fixup() validation fails. The caller,
ntfs_icx_ib_sync_write(), interprets any error as a write failure
requiring rollback. It does not differentiate between I/O errors and
validation failures, and calls post_write_mst_fixup() anyway.

Since post_write_mst_fixup() assumes that the index_block contents is
correct, it doesn't perform the boundary checks, which results in
out-of-bounds memory access.

An attacker can craft a malicious NTFS image with:
  - large index_block.usa_ofs offset, pointing outside the ntfs_record
  - index_block.usa_count = 0, causing integer underflow
  - or index_block.usa_count larger than actual number of sectors in the
    ntfs_record, causing out-of-bounds access

KASAN reports describing the memory corruption:
  ==================================================================
  BUG: KASAN: slab-out-of-bounds in post_write_mst_fixup+0x19c/0x1d0
  Read of size 2 at addr ffff8881586c9018 by task p/9428
  Call Trace:
   <TASK>
   dump_stack_lvl+0x100/0x190
   print_report+0x139/0x4ad
   ? post_write_mst_fixup+0x19c/0x1d0
   ? __virt_addr_valid+0x262/0x500
   ? post_write_mst_fixup+0x19c/0x1d0
   kasan_report+0xe4/0x1d0
   ? post_write_mst_fixup+0x19c/0x1d0
   post_write_mst_fixup+0x19c/0x1d0
   ntfs_icx_ib_sync_write+0x179/0x220
   ntfs_inode_sync_filename+0x83d/0x1080
   __ntfs_write_inode+0x1049/0x1480
   ntfs_file_fsync+0x131/0x9b0
  ==================================================================
  BUG: KASAN: slab-out-of-bounds in post_write_mst_fixup+0x1aa/0x1d0
  Write of size 2 at addr ffff8881586c91fe by task p/9428
  Call Trace:
   <TASK>
   dump_stack_lvl+0x100/0x190
   print_report+0x139/0x4ad
   ? post_write_mst_fixup+0x1aa/0x1d0
   ? __virt_addr_valid+0x262/0x500
   ? post_write_mst_fixup+0x1aa/0x1d0
   kasan_report+0xe4/0x1d0
   ? post_write_mst_fixup+0x1aa/0x1d0
   post_write_mst_fixup+0x1aa/0x1d0
   ntfs_icx_ib_sync_write+0x179/0x220
   ntfs_inode_sync_filename+0x83d/0x1080
   __ntfs_write_inode+0x1049/0x1480
   ntfs_file_fsync+0x131/0x9b0
  ==================================================================

Let's move the post_write_mst_fixup() call to ntfs_ib_write().
The ntfs_ib_write() function calls pre_write_mst_fixup() at the beginning.
If the index_block contents is invalid, pre_write_mst_fixup() fails and
ntfs_ib_write() returns early without calling post_write_mst_fixup() on
bad index_block.

## References
- https://git.kernel.org/stable/c/5b6eedd7cc2936f9238e852b553a1b326105bde8
- https://git.kernel.org/stable/c/e2018628301a6d9f54e34b0cb417f1688c66df1d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64431.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64431
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
