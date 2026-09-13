# [H] writeback: fix race between cgroup_writeback_umount() and inode_switch_wbs()

## Summary
Severity: High
Advisory: CVE-2026-64378
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64378
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <5.10.261, >=5.11.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

writeback: fix race between cgroup_writeback_umount() and inode_switch_wbs()

When a container exits, the following BUG_ON() is occasionally triggered:

==================================================================
 VFS: Busy inodes after unmount of sdb (ext4)
 ------------[ cut here ]------------
 kernel BUG at fs/super.c:695!
 CPU: 3 PID: 6 Comm: containerd-shim Tainted: G OE K 6.6 #1
 pstate: 63400009 (nZCv daif +PAN -UAO +TCO +DIT -SSBS BTYPE=--)
 pc : generic_shutdown_super+0xf0/0x100
 lr : generic_shutdown_super+0xf0/0x100
 Call trace:
  generic_shutdown_super+0xf0/0x100
  kill_block_super+0x20/0x48
  ext4_kill_sb+0x28/0x60
  deactivate_locked_super+0x54/0x130
  deactivate_super+0x84/0xa0
  cleanup_mnt+0xa4/0x140
  __cleanup_mnt+0x18/0x28
  task_work_run+0x78/0xe0
  do_notify_resume+0x204/0x240
==================================================================

The root cause is a race between cgroup_writeback_umount() and
inode_switch_wbs()/cleanup_offline_cgwb(). There is a window between
inode_prepare_wbs_switch() returning true and the subsequent
wb_queue_isw() call. Following is the process that triggers the issue:

      CPU A (umount)           |          CPU B (writeback)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                 inode_switch_wbs/cleanup_offline_cgwb
                                  atomic_inc(&isw_nr_in_flight)
                                  inode_prepare_wbs_switch
                                   -> passes SB_ACTIVE check
                                   __iget(inode)
 generic_shutdown_super
  sb->s_flags &= ~SB_ACTIVE
  cgroup_writeback_umount(sb)
   smp_mb()
   atomic_read(&isw_nr_in_flight)
   rcu_barrier()
    -> no pending RCU callbacks
   flush_workqueue(isw_wq)
    -> nothing queued, returns
  evict_inodes(sb)
   -> Inode skipped as isw still holds a ref.
  sop->put_super(sb)
   /* destroys percpu counters */
  -> VFS: Busy inodes after unmount!
                                  wb_queue_isw()
                                   queue_work(isw_wq, ...)
                                  /* later in work function */
                                  inode_switch_wbs_work_fn
                                   process_inode_switch_wbs
                                    iput() -> evict
                                     percpu_counter_dec() // UAF!

Fix this by extending the RCU read-side critical section in
inode_switch_wbs() and cleanup_offline_cgwb() to cover from
inode_prepare_wbs_switch() through wb_queue_isw().  Since there is
no sleep in this window, rcu_read_lock() can be used.  Then add a
synchronize_rcu() in cgroup_writeback_umount() before the existing
rcu_barrier(), so that all in-flight switchers that have passed the
SB_ACTIVE check have completed queue_work() before flush_workqueue()
is called.

The existing rcu_barrier() is intentionally retained so this fix can
be backported unchanged to stable kernels (5.10.y, 6.6.y, ...) that
still queue switches via queue_rcu_work(). It is a no-op on current
mainline (since commit e1b849cfa6b6 ("writeback: Avoid contention on
wb->list_lock when switching inodes")) and is removed in a follow-up
patch.

## References
- https://git.kernel.org/stable/c/087d5b8b501c570f84bf655164e6698c3ce146e0
- https://git.kernel.org/stable/c/3c9c9648f77e4d14e50676bc51c2174ba9c8d361
- https://git.kernel.org/stable/c/53eeaf4d63068dbc7708b0c7adb20151c812feca
- https://git.kernel.org/stable/c/5c3265f3252b2ee50707adaaa3f9bd0df3df72de
- https://git.kernel.org/stable/c/685fc15a410885b6d4dee64de0dce721b9428b12
- https://git.kernel.org/stable/c/c923cc3cb5cd8945ceaf08252754110643446593
- https://git.kernel.org/stable/c/cba38ec4cbd3a7b8b942a8d52531a05be8a9ff0d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64378.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64378
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
