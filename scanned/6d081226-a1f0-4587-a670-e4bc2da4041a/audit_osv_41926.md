# [H] cifs: Fix busy dentry used after unmounting

## Summary
Severity: High
Advisory: CVE-2026-64108
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64108
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: Fix busy dentry used after unmounting

Since commit 340cea84f691c ("cifs: open files should not hold ref on
superblock"), cifs file only holds the dentry ref_cnt, the cifs file
close work(cfile->deferred) could be executed after unmounting, which
will trigger a warning in generic_shutdown_super:
 BUG: Dentry 00000000a14a6845{i=c,n=file}  still in use (1) [unmount of
 cifs cifs]

The detailed processs is:
   process A           process B           kworker
 fd = open(PATH)
  vfs_open
   file->__f_path = *path // dentry->d_lockref.count = 1
   cifs_open
    cifs_new_fileinfo
     cfile->dentry = dget(dentry) // dentry->d_lockref.count = 2
 close(fd)
  __fput
  cifs_close
   queue_delayed_work(deferredclose_wq, cfile->deferred)
  dput(dentry) // dentry->d_lockref.count = 1
			                 smb2_deferred_work_close
					  _cifsFileInfo_put
					   list_del(&cifs_file->flist)
                    umount
		     cleanup_mnt
		      deactivate_super
		       cifs_kill_sb
		        cifs_close_all_deferred_files_sb
			 cifs_close_all_deferred_files
			  // cannot find cfile, skip _cifsFileInfo_put
			kill_anon_super
			 generic_shutdown_super
			  shrink_dcache_for_umount
			   umount_check
			    WARN ! // dentry->d_lockref.count = 1
					   cifsFileInfo_put_final
					    dput(cifs_file->dentry)
		                            // dentry->d_lockref.count = 0

Fix it by flushing 'deferredclose_wq' before calling kill_anon_super.

Fetch a reproducer in https://bugzilla.kernel.org/show_bug.cgi?id=221548.

## References
- https://git.kernel.org/stable/c/5e7d9d0805e58fa3760894e73115b7a74024fd07
- https://git.kernel.org/stable/c/bdc349a87f1fb02c18c4071858a06542bfea783d
- https://git.kernel.org/stable/c/c68337442f03953237a94577beb468ab2662a851
- https://git.kernel.org/stable/c/c7364cea52531534676b9f7dbc0a477c11f4c050
- https://git.kernel.org/stable/c/e1ffa6cf662383f95816eed1b623429d82675e75
- https://git.kernel.org/stable/c/f2deaa2f409a4598eaa10f2a93a676c0632af248
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64108.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64108
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
