# [H] f2fs: fix fsck inconsistency caused by incorrect nat_entry flag usage

## Summary
Severity: High
Advisory: CVE-2026-53368
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53368
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix fsck inconsistency caused by incorrect nat_entry flag usage

f2fs_need_dentry_mark() reads nat_entry flags without mutual exclusion
with the checkpoint path, which can result in an incorrect inode block
marking state. The scenario is as follows:

create & write & fsync 'file A'                 write checkpoint
- f2fs_do_sync_file // inline inode
 - f2fs_write_inode // inode folio is dirty
                                                - f2fs_write_checkpoint
                                                 - f2fs_flush_merged_writes
                                                 - f2fs_sync_node_pages
 - f2fs_fsync_node_pages // no dirty node
 - f2fs_need_inode_block_update // return true
 - f2fs_fsync_node_pages // inode dirtied
  - f2fs_need_dentry_mark //return true
                                                 - f2fs_flush_nat_entries
                                                - f2fs_write_checkpoint end
  - __write_node_folio // inode with DENT_BIT_SHIFT set
  SPO, "fsck --dry-run" find inode has already checkpointed but still
  with DENT_BIT_SHIFT set

The state observed by f2fs_need_dentry_mark() can differ from the state
observed in __write_node_folio() after acquiring sbi->node_write. The
root cause is that the semantics of IS_CHECKPOINTED and
HAS_FSYNCED_INODE are only guaranteed after the checkpoint write has
fully completed.

This patch moves set_dentry_mark() into __write_node_folio() and
protects it with the sbi->node_write lock.

## References
- https://git.kernel.org/stable/c/019f9dda7f66e55eb94cd32e1d3fff5835f73fbc
- https://git.kernel.org/stable/c/b28a83ea4934215b5de906c3ee4fbfbc651573e0
- https://git.kernel.org/stable/c/bedb710b63ae1bd617e65d0a8cf6cea1200b3753
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53368.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53368
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
