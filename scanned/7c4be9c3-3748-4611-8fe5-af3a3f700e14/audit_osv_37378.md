# [H] ext4: fix use-after-free in update_super_work when racing with umount

## Summary
Severity: High
Advisory: CVE-2026-31446
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31446
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.203, >=5.16.0 <6.1.168, >=5.18.0 <6.6.131, >=6.2.0 <6.12.80, >=6.7.0 <6.18.21, >=6.13.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix use-after-free in update_super_work when racing with umount

Commit b98535d09179 ("ext4: fix bug_on in start_this_handle during umount
filesystem") moved ext4_unregister_sysfs() before flushing s_sb_upd_work
to prevent new error work from being queued via /proc/fs/ext4/xx/mb_groups
reads during unmount. However, this introduced a use-after-free because
update_super_work calls ext4_notify_error_sysfs() -> sysfs_notify() which
accesses the kobject's kernfs_node after it has been freed by kobject_del()
in ext4_unregister_sysfs():

  update_super_work                ext4_put_super
  -----------------                --------------
                                   ext4_unregister_sysfs(sb)
                                     kobject_del(&sbi->s_kobj)
                                       __kobject_del()
                                         sysfs_remove_dir()
                                           kobj->sd = NULL
                                         sysfs_put(sd)
                                           kernfs_put()  // RCU free
  ext4_notify_error_sysfs(sbi)
    sysfs_notify(&sbi->s_kobj)
      kn = kobj->sd              // stale pointer
      kernfs_get(kn)             // UAF on freed kernfs_node
                                   ext4_journal_destroy()
                                     flush_work(&sbi->s_sb_upd_work)

Instead of reordering the teardown sequence, fix this by making
ext4_notify_error_sysfs() detect that sysfs has already been torn down
by checking s_kobj.state_in_sysfs, and skipping the sysfs_notify() call
in that case. A dedicated mutex (s_error_notify_mutex) serializes
ext4_notify_error_sysfs() against kobject_del() in ext4_unregister_sysfs()
to prevent TOCTOU races where the kobject could be deleted between the
state_in_sysfs check and the sysfs_notify() call.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/034053378dd81837fd6c7a43b37ee2e58d4f0b4e
- https://git.kernel.org/stable/c/08b10e6f37fc533a759e9833af0692242e8b3f93
- https://git.kernel.org/stable/c/9449f99ba04f5dd1c8423ad8a90b3651d7240d1d
- https://git.kernel.org/stable/c/c4d829737329f2290dd41e290b7d75effdb2a7ff
- https://git.kernel.org/stable/c/c8fe17a1b308c3d8c703ebfb049b325f844342c3
- https://git.kernel.org/stable/c/c97e282f7bfd0c3554c63d289964a5ca6a1d2ffe
- https://git.kernel.org/stable/c/d15e4b0a418537aafa56b2cb80d44add83e83697
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31446.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31446
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
