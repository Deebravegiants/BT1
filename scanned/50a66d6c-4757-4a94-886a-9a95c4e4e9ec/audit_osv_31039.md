# [H] RDMA/rxe: Remove the direct link to net_device

## Summary
Severity: High
Advisory: CVE-2024-57795
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-15
Source: https://osv.dev/vulnerability/CVE-2024-57795
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <6.6.120, >=6.7.0 <6.12.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rxe: Remove the direct link to net_device

The similar patch in siw is in the link:
https://git.kernel.org/rdma/rdma/c/16b87037b48889

This problem also occurred in RXE. The following analyze this problem.
In the following Call Traces:
"
BUG: KASAN: slab-use-after-free in dev_get_flags+0x188/0x1d0 net/core/dev.c:8782
Read of size 4 at addr ffff8880554640b0 by task kworker/1:4/5295

CPU: 1 UID: 0 PID: 5295 Comm: kworker/1:4 Not tainted
6.12.0-rc3-syzkaller-00399-g9197b73fd7bb #0
Hardware name: Google Compute Engine/Google Compute Engine,
BIOS Google 09/13/2024
Workqueue: infiniband ib_cache_event_task
Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:94 [inline]
 dump_stack_lvl+0x241/0x360 lib/dump_stack.c:120
 print_address_description mm/kasan/report.c:377 [inline]
 print_report+0x169/0x550 mm/kasan/report.c:488
 kasan_report+0x143/0x180 mm/kasan/report.c:601
 dev_get_flags+0x188/0x1d0 net/core/dev.c:8782
 rxe_query_port+0x12d/0x260 drivers/infiniband/sw/rxe/rxe_verbs.c:60
 __ib_query_port drivers/infiniband/core/device.c:2111 [inline]
 ib_query_port+0x168/0x7d0 drivers/infiniband/core/device.c:2143
 ib_cache_update+0x1a9/0xb80 drivers/infiniband/core/cache.c:1494
 ib_cache_event_task+0xf3/0x1e0 drivers/infiniband/core/cache.c:1568
 process_one_work kernel/workqueue.c:3229 [inline]
 process_scheduled_works+0xa65/0x1850 kernel/workqueue.c:3310
 worker_thread+0x870/0xd30 kernel/workqueue.c:3391
 kthread+0x2f2/0x390 kernel/kthread.c:389
 ret_from_fork+0x4d/0x80 arch/x86/kernel/process.c:147
 ret_from_fork_asm+0x1a/0x30 arch/x86/entry/entry_64.S:244
 </TASK>
"

1). In the link [1],

"
 infiniband syz2: set down
"

This means that on 839.350575, the event ib_cache_event_task was sent andi
queued in ib_wq.

2). In the link [1],

"
 team0 (unregistering): Port device team_slave_0 removed
"

It indicates that before 843.251853, the net device should be freed.

3). In the link [1],

"
 BUG: KASAN: slab-use-after-free in dev_get_flags+0x188/0x1d0
"

This means that on 850.559070, this slab-use-after-free problem occurred.

In all, on 839.350575, the event ib_cache_event_task was sent and queued
in ib_wq,

before 843.251853, the net device veth was freed.

on 850.559070, this event was executed, and the mentioned freed net device
was called. Thus, the above call trace occurred.

[1] https://syzkaller.appspot.com/x/log.txt?x=12e7025f980000

## References
- https://git.kernel.org/stable/c/2ac5415022d16d63d912a39a06f32f1f51140261
- https://git.kernel.org/stable/c/32ca3557d968e662957131374a5f81c9c9cdbba8
- https://git.kernel.org/stable/c/9f6f54e6a6863131442b40e14d1792b090c7ce21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57795.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57795
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
