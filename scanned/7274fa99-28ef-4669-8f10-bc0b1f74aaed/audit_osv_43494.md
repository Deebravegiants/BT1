# [H] net: watchdog: fix refcount tracking races

## Summary
Severity: High
Advisory: CVE-2026-74264
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74264
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: watchdog: fix refcount tracking races

Blamed commit converted the untracked dev_hold()/dev_put() calls
in the watchdog code to use the tracked dev_hold_track()/dev_put_track()
(which were later renamed/interfaced to netdev_hold() and netdev_put()).

By introducing dev->watchdog_dev_tracker to store the
reference tracking information without adding synchronization
between netdev_watchdog_up() and dev_watchdog(), it enabled the
race condition where this pointer could be overwritten or freed
concurrently, leading to the list corruption crash syzbot reported:

list_del corruption, ffff888114a18c00->next is NULL
 kernel BUG at lib/list_debug.c:52 !
Oops: invalid opcode: 0000 [#1] SMP KASAN PTI
CPU: 1 UID: 0 PID: 91 Comm: kworker/u8:5 Not tainted syzkaller #0 PREEMPT(lazy)
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 05/09/2026
Workqueue: events_unbound linkwatch_event
 RIP: 0010:__list_del_entry_valid_or_report.cold+0x22/0x2a lib/list_debug.c:52
Call Trace:
 <TASK>
  __list_del_entry_valid include/linux/list.h:132 [inline]
  __list_del_entry include/linux/list.h:246 [inline]
  list_move_tail include/linux/list.h:341 [inline]
  ref_tracker_free+0x1a7/0x6c0 lib/ref_tracker.c:329
  netdev_tracker_free include/linux/netdevice.h:4491 [inline]
  netdev_put include/linux/netdevice.h:4508 [inline]
  netdev_put include/linux/netdevice.h:4504 [inline]
  netdev_watchdog_down net/sched/sch_generic.c:600 [inline]
  dev_deactivate_many+0x28c/0xfe0 net/sched/sch_generic.c:1363
  dev_deactivate+0x109/0x1d0 net/sched/sch_generic.c:1397
  linkwatch_do_dev net/core/link_watch.c:184 [inline]
  linkwatch_do_dev+0xd3/0x120 net/core/link_watch.c:166
  __linkwatch_run_queue+0x3a5/0x810 net/core/link_watch.c:240
  linkwatch_event+0x8f/0xc0 net/core/link_watch.c:314
  process_one_work+0xa0e/0x1980 kernel/workqueue.c:3314
  process_scheduled_works kernel/workqueue.c:3397 [inline]
  worker_thread+0x5ef/0xe50 kernel/workqueue.c:3478
  kthread+0x370/0x450 kernel/kthread.c:436
  ret_from_fork+0x69a/0xc80 arch/x86/kernel/process.c:158
  ret_from_fork_asm+0x1a/0x30 arch/x86/entry/entry_64.S:245

This patch has three coordinated parts:

1) Add dev->watchdog_lock and dev->watchdog_ref_held to serialize watchdog operations.

2) Remove netdev_watchdog_up() call from netif_carrier_on():
   This ensures netdev_watchdog_up() is only called from process/BH context
   (via linkwatch workqueue dev_activate()), allowing us to use
   spin_lock_bh() for synchronization.

3) Synchronize watchdog up and watchdog timer:
   Protect netdev_watchdog_up() with tx_global_lock and watchdog_lock.
   Only allocate a new tracker in netdev_watchdog_up() if one is
   not already present.
   In dev_watchdog(), ensure we don't release the tracker if the
   timer was rescheduled either by dev_watchdog() itself or concurrently
   by netdev_watchdog_up().

## References
- https://git.kernel.org/stable/c/446fe8ce699ce0a4d702f7b0fcdb50de340b9260
- https://git.kernel.org/stable/c/7ce2b00ff058ec4cafc9b447e1f0a6d6f49275d9
- https://git.kernel.org/stable/c/8eed5519e496b7a07f441a0f579cb228a33189f7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74264.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74264
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
