# [H] f2fs: fix fsck inconsistency caused by FGGC of node block

## Summary
Severity: High
Advisory: CVE-2026-46175
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46175
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix fsck inconsistency caused by FGGC of node block

During FGGC node block migration, fsck may incorrectly treat the
migrated node block as fsync-written data.

The reproduction scenario:
root@vm:/mnt/f2fs# seq 1 2048 | xargs -n 1 ./test_sync // write inline inode and sync
root@vm:/mnt/f2fs# rm -f 1
root@vm:/mnt/f2fs# sync
root@vm:/mnt/f2fs# f2fs_io gc_range // move data block in sync mode and not write CP
  SPO, "fsck --dry-run" find inode has already checkpointed but still
  with DENT_BIT_SHIFT set

The root cause is that GC does not clear the dentry mark and fsync mark
during node block migration, leading fsck to misinterpret them as
user-issued fsync writes.

In BGGC mode, node block migration is handled by f2fs_sync_node_pages(),
which guarantees the dentry and fsync marks are cleared before writing.

This patch move the set/clear of the fsync|dentry marks into
__write_node_folio to make the logic clearer, and ensures the
fsync|dentry mark is cleared in FGGC.

## References
- https://git.kernel.org/stable/c/8be551f538dc5b64183e27bd45a7a0795263f760
- https://git.kernel.org/stable/c/c3e238bd1f56993f205ef83889d406dfeaf717a8
- https://git.kernel.org/stable/c/e7c6d30169b03307d27c4479563df79c08f3a746
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46175.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46175
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
