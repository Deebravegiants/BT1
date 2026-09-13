# [H] linkwatch: use __dev_put() in callers to prevent UAF

## Summary
Severity: High
Advisory: CVE-2026-23192
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-14
Source: https://osv.dev/vulnerability/CVE-2026-23192
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

linkwatch: use __dev_put() in callers to prevent UAF

After linkwatch_do_dev() calls __dev_put() to release the linkwatch
reference, the device refcount may drop to 1. At this point,
netdev_run_todo() can proceed (since linkwatch_sync_dev() sees an
empty list and returns without blocking), wait for the refcount to
become 1 via netdev_wait_allrefs_any(), and then free the device
via kobject_put().

This creates a use-after-free when __linkwatch_run_queue() tries to
call netdev_unlock_ops() on the already-freed device.

Note that adding netdev_lock_ops()/netdev_unlock_ops() pair in
netdev_run_todo() before kobject_put() would not work, because
netdev_lock_ops() is conditional - it only locks when
netdev_need_ops_lock() returns true. If the device doesn't require
ops_lock, linkwatch won't hold any lock, and netdev_run_todo()
acquiring the lock won't provide synchronization.

Fix this by moving __dev_put() from linkwatch_do_dev() to its
callers. The device reference logically pairs with de-listing the
device, so it's reasonable for the caller that did the de-listing
to release it. This allows placing __dev_put() after all device
accesses are complete, preventing UAF.

The bug can be reproduced by adding mdelay(2000) after
linkwatch_do_dev() in __linkwatch_run_queue(), then running:

  ip tuntap add mode tun name tun_test
  ip link set tun_test up
  ip link set tun_test carrier off
  ip link set tun_test carrier on
  sleep 0.5
  ip tuntap del mode tun name tun_test

KASAN report:

 ==================================================================
 BUG: KASAN: use-after-free in netdev_need_ops_lock include/net/netdev_lock.h:33 [inline]
 BUG: KASAN: use-after-free in netdev_unlock_ops include/net/netdev_lock.h:47 [inline]
 BUG: KASAN: use-after-free in __linkwatch_run_queue+0x865/0x8a0 net/core/link_watch.c:245
 Read of size 8 at addr ffff88804de5c008 by task kworker/u32:10/8123

 CPU: 0 UID: 0 PID: 8123 Comm: kworker/u32:10 Not tainted syzkaller #0 PREEMPT(full)
 Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 1.16.3-debian-1.16.3-2 04/01/2014
 Workqueue: events_unbound linkwatch_event
 Call Trace:
  <TASK>
  __dump_stack lib/dump_stack.c:94 [inline]
  dump_stack_lvl+0x100/0x190 lib/dump_stack.c:120
  print_address_description mm/kasan/report.c:378 [inline]
  print_report+0x156/0x4c9 mm/kasan/report.c:482
  kasan_report+0xdf/0x1a0 mm/kasan/report.c:595
  netdev_need_ops_lock include/net/netdev_lock.h:33 [inline]
  netdev_unlock_ops include/net/netdev_lock.h:47 [inline]
  __linkwatch_run_queue+0x865/0x8a0 net/core/link_watch.c:245
  linkwatch_event+0x8f/0xc0 net/core/link_watch.c:304
  process_one_work+0x9c2/0x1840 kernel/workqueue.c:3257
  process_scheduled_works kernel/workqueue.c:3340 [inline]
  worker_thread+0x5da/0xe40 kernel/workqueue.c:3421
  kthread+0x3b3/0x730 kernel/kthread.c:463
  ret_from_fork+0x754/0xaf0 arch/x86/kernel/process.c:158
  ret_from_fork_asm+0x1a/0x30 arch/x86/entry/entry_64.S:246
  </TASK>
 ==================================================================

## References
- https://git.kernel.org/stable/c/2718ae6af7445ba2ee0abf6365ca43a9a3b16aeb
- https://git.kernel.org/stable/c/83b67cc9be9223183caf91826d9c194d7fb128fa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23192.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23192
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
