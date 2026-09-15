# [H] afs: Fix reinitialisation of the inode, in particular ->lock_work

## Summary
Severity: High
Advisory: CVE-2026-72375
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72375
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.23 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

afs: Fix reinitialisation of the inode, in particular ->lock_work

It seems that initalising afs_vnode::lock_work a single time in the slab's
init function isn't sufficient for work_structs.  This results in the
DEBUG_OBJECTS debugging stuff producing a warning occasionally when running
the generic/131 xfstest:

 ODEBUG: activate not available (active state 0) object: 0000000016d8760f object type: work_struct hint: afs_lock_work+0x0/0x220
 WARNING: lib/debugobjects.c:629 at debug_print_object+0x4b/0x90, CPU#3: locktest/7695
 ...
 CPU: 3 UID: 0 PID: 7695 Comm: locktest Tainted: G S                  7.1.0-build3+ #2771 PREEMPT
 ...
 RIP: 0010:debug_print_object+0x65/0x90
 ...
 Call Trace:
  <TASK>
  ? __pfx_afs_lock_work+0x10/0x10
  debug_object_activate+0x122/0x170
  insert_work+0x25/0x60
  __queue_work+0x2e0/0x340
  queue_delayed_work_on+0x48/0x70
  afs_fl_release_private+0x57/0x70
  locks_release_private+0x5c/0xa0
  locks_free_lock+0xe/0x20
  posix_lock_inode+0x55f/0x5b0
  locks_lock_inode_wait+0x81/0x140
  ? file_write_and_wait_range+0x50/0x70
  afs_lock+0xcd/0x110
  fcntl_setlk+0x10d/0x260
  do_fcntl+0x24e/0x5b0
  __do_sys_fcntl+0x6a/0x90
  do_syscall_64+0x11e/0x310
  entry_SYSCALL_64_after_hwframe+0x71/0x79

Fix this by reinitialising ->lock_work after allocating an inode.

Also, flush ->lock_work when the inode is being evicted to make sure it's
not still running.

## References
- https://git.kernel.org/stable/c/5597fbd1e7c161914f20315a726e54025b0fdadb
- https://git.kernel.org/stable/c/63d3f283858fae097fb09ddd4ce46bb0bc1f9d01
- https://git.kernel.org/stable/c/ebfd13c0367adb43d7c0a72f5cd7e004e60c6b28
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72375.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72375
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
