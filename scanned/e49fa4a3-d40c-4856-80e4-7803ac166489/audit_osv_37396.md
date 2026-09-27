# [H] ksmbd: fix memory leaks and NULL deref in smb2_lock()

## Summary
Severity: High
Advisory: CVE-2026-31477
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31477
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.168, >=6.2.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix memory leaks and NULL deref in smb2_lock()

smb2_lock() has three error handling issues after list_del() detaches
smb_lock from lock_list at no_check_cl:

1) If vfs_lock_file() returns an unexpected error in the non-UNLOCK
   path, goto out leaks smb_lock and its flock because the out:
   handler only iterates lock_list and rollback_list, neither of
   which contains the detached smb_lock.

2) If vfs_lock_file() returns -ENOENT in the UNLOCK path, goto out
   leaks smb_lock and flock for the same reason.  The error code
   returned to the dispatcher is also stale.

3) In the rollback path, smb_flock_init() can return NULL on
   allocation failure.  The result is dereferenced unconditionally,
   causing a kernel NULL pointer dereference.  Add a NULL check to
   prevent the crash and clean up the bookkeeping; the VFS lock
   itself cannot be rolled back without the allocation and will be
   released at file or connection teardown.

Fix cases 1 and 2 by hoisting the locks_free_lock()/kfree() to before
the if(!rc) check in the UNLOCK branch so all exit paths share one
free site, and by freeing smb_lock and flock before goto out in the
non-UNLOCK branch.  Propagate the correct error code in both cases.
Fix case 3 by wrapping the VFS unlock in an if(rlock) guard and adding
a NULL check for locks_free_lock(rlock) in the shared cleanup.

Found via call-graph analysis using sqry.

## References
- https://git.kernel.org/stable/c/309b44ed684496ed3f9c5715d10b899338623512
- https://git.kernel.org/stable/c/3cdacd11b41569ce75b3162142240f2355e04900
- https://git.kernel.org/stable/c/91aeaa7256006d79a37298f5a1df23325db91599
- https://git.kernel.org/stable/c/aab42f0795620cf0d3955a520f571f697d0f9a2a
- https://git.kernel.org/stable/c/c9b95ef6f5039f19e46c3a521a4fe1752d91dfe9
- https://git.kernel.org/stable/c/cdac6f7e7e428dc70e3b5898ac6999a72ed13993
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31477.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31477
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
