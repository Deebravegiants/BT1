# [M] ovl: fix null pointer dereference in ovl_permission()

## Summary
Severity: Medium
Advisory: CVE-2023-53260
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53260
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.43, >=6.2.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ovl: fix null pointer dereference in ovl_permission()

Following process:
          P1                     P2
 path_lookupat
  link_path_walk
   inode_permission
    ovl_permission
      ovl_i_path_real(inode, &realpath)
        path->dentry = ovl_i_dentry_upper(inode)
                          drop_cache
			   __dentry_kill(ovl_dentry)
		            iput(ovl_inode)
		             ovl_destroy_inode(ovl_inode)
		              dput(oi->__upperdentry)
		               dentry_kill(upperdentry)
		                dentry_unlink_inode
				 upperdentry->d_inode = NULL
      realinode = d_inode(realpath.dentry) // return NULL
      inode_permission(realinode)
       inode->i_sb  // NULL pointer dereference
, will trigger an null pointer dereference at realinode:
  [  335.664979] BUG: kernel NULL pointer dereference,
                 address: 0000000000000002
  [  335.668032] CPU: 0 PID: 2592 Comm: ls Not tainted 6.3.0
  [  335.669956] RIP: 0010:inode_permission+0x33/0x2c0
  [  335.678939] Call Trace:
  [  335.679165]  <TASK>
  [  335.679371]  ovl_permission+0xde/0x320
  [  335.679723]  inode_permission+0x15e/0x2c0
  [  335.680090]  link_path_walk+0x115/0x550
  [  335.680771]  path_lookupat.isra.0+0xb2/0x200
  [  335.681170]  filename_lookup+0xda/0x240
  [  335.681922]  vfs_statx+0xa6/0x1f0
  [  335.682233]  vfs_fstatat+0x7b/0xb0

Fetch a reproducer in [Link].

Use the helper ovl_i_path_realinode() to get realinode and then do
non-nullptr checking.

## References
- https://git.kernel.org/stable/c/1a73f5b8f079fd42a544c1600beface50c63af7c
- https://git.kernel.org/stable/c/53dd2ca2c02fdcfe3aad2345091d371063f97d17
- https://git.kernel.org/stable/c/69f9ae7edf9ec0ff500429101923347fcba5c8c4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53260.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53260
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
