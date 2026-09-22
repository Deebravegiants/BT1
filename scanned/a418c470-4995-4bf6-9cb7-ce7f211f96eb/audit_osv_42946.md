# [H] ntfs: skip extent mft records in writeback to prevent deadlock

## Summary
Severity: High
Advisory: CVE-2026-72203
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72203
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <6.9, >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: skip extent mft records in writeback to prevent deadlock

This patch fixes the ABBA deadlock between extent_lock and extent
mrec_lock triggered by xfstests generic/113, that occurs since the commit
6994acf33bae ("ntfs: use base mft_no when looking up base inode for
		extent record").

Path A (inode writeback):
  VFS writeback
    -> ntfs_write_inode()
      -> __ntfs_write_inode()
        -> mutex_lock(&ni->extent_lock)
        -> mutex_lock(&tni->mrec_lock)

Path B (MFT folio writeback):
  VFS writeback of $MFT dirty folios
    -> ntfs_mft_writepages()
      -> ntfs_write_mft_block()
        -> ntfs_may_write_mft_record()
          -> holds one extent mrec_lock from a previous iteration
          -> tries to acquire another base inode extent_lock

By removing all extent_lock and extent mrec_lock acquisition from the MFT
folio writeback path, the ABBA lock ordering is eliminated:

Path A: __ntfs_write_inode(): extent_lock -> mrec_lock
Path B (removed): ntfs_write_mft_block(): mrec_lock -> extent_lock

Path B is always redundant for extent records because:

1. mark_mft_record_dirty(ext_ni) does NOT dirty the MFT folio.
   It only sets NInoDirty(ext_ni) and marks the base VFS inode dirty
   via __mark_inode_dirty(I_DIRTY_DATASYNC), which triggers Path A.
   Therefore, normal extent modifications never create a situation where
   the MFT folio is dirty and Path B is not scheduled.

2. The MFT folio only gets dirtied via ntfs_mft_mark_dirty() inside
   ntfs_mft_record_alloc(). But all identified callers in attrib.c
   (ntfs_attr_add, ntfs_attr_record_move_away,
   ntfs_attr_make_non_resident, ntfs_attr_record_resize) follow through
   with mark_mft_record_dirty(), which triggers Path A to write the
   complete record.

3. ntfs_evict_big_inode() calls ntfs_commit_inode() before freeing extent
   inodes, ensuring all dirty extents are flushed via Path A before the
   base inode leaves the icache.

## References
- https://git.kernel.org/stable/c/76bc14c7097ff678b2b5dbfd4fa33b46897d87ce
- https://git.kernel.org/stable/c/7ffa8f3d30236e0ab897c30bdb01224ff1fe1c89
- https://git.kernel.org/stable/c/f831ab09d521898bf1dd99bf5adfd630ea1428e3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72203.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72203
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
