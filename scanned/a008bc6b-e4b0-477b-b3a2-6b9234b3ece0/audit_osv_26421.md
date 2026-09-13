# [H] net: caif: Fix use-after-free in cfusbl_device_notify()

## Summary
Severity: High
Advisory: CVE-2023-53138
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-02
Source: https://osv.dev/vulnerability/CVE-2023-53138
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.3.0 <4.14.310, >=4.15.0 <4.19.278, >=4.20.0 <5.4.237, >=5.5.0 <5.10.175, >=5.11.0 <5.15.103, >=5.16.0 <6.1.20, >=6.2.0 <6.2.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: caif: Fix use-after-free in cfusbl_device_notify()

syzbot reported use-after-free in cfusbl_device_notify() [1].  This
causes a stack trace like below:

BUG: KASAN: use-after-free in cfusbl_device_notify+0x7c9/0x870 net/caif/caif_usb.c:138
Read of size 8 at addr ffff88807ac4e6f0 by task kworker/u4:6/1214

CPU: 0 PID: 1214 Comm: kworker/u4:6 Not tainted 5.19.0-rc3-syzkaller-00146-g92f20ff72066 #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 01/01/2011
Workqueue: netns cleanup_net
Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:88 [inline]
 dump_stack_lvl+0xcd/0x134 lib/dump_stack.c:106
 print_address_description.constprop.0.cold+0xeb/0x467 mm/kasan/report.c:313
 print_report mm/kasan/report.c:429 [inline]
 kasan_report.cold+0xf4/0x1c6 mm/kasan/report.c:491
 cfusbl_device_notify+0x7c9/0x870 net/caif/caif_usb.c:138
 notifier_call_chain+0xb5/0x200 kernel/notifier.c:87
 call_netdevice_notifiers_info+0xb5/0x130 net/core/dev.c:1945
 call_netdevice_notifiers_extack net/core/dev.c:1983 [inline]
 call_netdevice_notifiers net/core/dev.c:1997 [inline]
 netdev_wait_allrefs_any net/core/dev.c:10227 [inline]
 netdev_run_todo+0xbc0/0x10f0 net/core/dev.c:10341
 default_device_exit_batch+0x44e/0x590 net/core/dev.c:11334
 ops_exit_list+0x125/0x170 net/core/net_namespace.c:167
 cleanup_net+0x4ea/0xb00 net/core/net_namespace.c:594
 process_one_work+0x996/0x1610 kernel/workqueue.c:2289
 worker_thread+0x665/0x1080 kernel/workqueue.c:2436
 kthread+0x2e9/0x3a0 kernel/kthread.c:376
 ret_from_fork+0x1f/0x30 arch/x86/entry/entry_64.S:302
 </TASK>

When unregistering a net device, unregister_netdevice_many_notify()
sets the device's reg_state to NETREG_UNREGISTERING, calls notifiers
with NETDEV_UNREGISTER, and adds the device to the todo list.

Later on, devices in the todo list are processed by netdev_run_todo().
netdev_run_todo() waits devices' reference count become 1 while
rebdoadcasting NETDEV_UNREGISTER notification.

When cfusbl_device_notify() is called with NETDEV_UNREGISTER multiple
times, the parent device might be freed.  This could cause UAF.
Processing NETDEV_UNREGISTER multiple times also causes inbalance of
reference count for the module.

This patch fixes the issue by accepting only first NETDEV_UNREGISTER
notification.

## References
- https://git.kernel.org/stable/c/1793da97a23e31c5bf06631f3f3e5a25f368fd64
- https://git.kernel.org/stable/c/287027d8a567168a5d8ce5cb0cba16a34791a48c
- https://git.kernel.org/stable/c/3f14457e1584224f4296af613bbd99deb60b5d91
- https://git.kernel.org/stable/c/68a45c3cf0e2242a533657f4f535d9b6a7447a79
- https://git.kernel.org/stable/c/9781e98a97110f5e76999058368b4be76a788484
- https://git.kernel.org/stable/c/9dc16be373b382ddd4c274052a6e870a95e76c01
- https://git.kernel.org/stable/c/c3aaec463a632cf4187dc017e421bfa69d7834a9
- https://git.kernel.org/stable/c/d1a11bbdbb5ea9f172019c5a4a3e9d8eabd72179
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53138.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53138
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
