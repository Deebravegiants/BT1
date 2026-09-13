# [H] smb: client: fix busy dentry warning on unmount after DIO

## Summary
Severity: High
Advisory: CVE-2026-72315
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72315
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix busy dentry warning on unmount after DIO

Commit c68337442f03 ("cifs: Fix busy dentry used after unmounting") fixed
the issue in cifs where deferred close of a file led to a dentry reference
count not being released in umount, by flushing deferredclose_wq in
cifs_kill_sb() to solve it.

However, the cifs DIO path suffers from the same busy-dentry problem caused
by a delayed dentry reference-count release:

	[dio]			[cifsd]			[close + umount]
netfs_unbuffered_write_iter_locked
...
				cifs_demultiplex_thread
 netfs_unbuffered_write
  cifs_issue_write
  netfs_wait_for_in_progress_stream [1]
				...
				 netfs_write_subrequest_terminated
				  netfs_subreq_clear_in_progress
				   netfs_wake_collector // wake [1]
				  netfs_put_subrequest
 netfs_put_request
  queue_work(system_dfl_wq, xxx) [2]
 // dio write return					cifs_close
							 _cifsFileInfo_put
							  // cfile->count 2->1
							  --cfile->count [3]

							// umount
							cifs_kill_sb
							 kill_anon_super
							  // warning triggered!
							  shrink_dcache_for_umount [4]
[system_dfl_wq] [5]
netfs_free_request
 ...
 _cifsFileInfo_put
  // cfile->count 1->0
  --cfile->count
  queue_work(fileinfo_put_wq, xxx)

[fileinfo_put_wq] [6]
cifsFileInfo_put_work
 cifsFileInfo_put_final
  dput

If the umount path is triggered before [5], it results warning:
BUG: Dentry 00000000eab1f070{i=9a917b66ae404fec,n=test}  still in use (1)
[unmount of cifs cifs]

The existing per-inode ictx->io_count wait in cifs_evict_inode() does not
help: it lives in the inode eviction path, which runs after
shrink_dcache_for_umount() has already warned about the busy dentries.

Fix it by adding a per-superblock outstanding-rreq counter that is
incremented in cifs_init_request() and decremented in cifs_free_request().
In cifs_kill_sb(), before kill_anon_super(), wait for this counter to reach
0 - which guarantees that all cleanup_work for this sb have run and thus
all relevant cfile puts are queued on fileinfo_put_wq or serverclose_wq.
Then drain the workqueue so the dentry refs are dropped.

This is a targeted wait, not a flush of the system-wide system_dfl_wq.

## References
- https://git.kernel.org/stable/c/75f5c412fa867efa0bf9b646bffe0d912109e84a
- https://git.kernel.org/stable/c/f0eac9c3c3711f24efc2aaf12b8ec3e54a38c214
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72315.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72315
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
