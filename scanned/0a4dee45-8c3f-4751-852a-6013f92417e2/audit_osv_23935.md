# [H] tipc: fix use-after-free Read in tipc_named_reinit

## Summary
Severity: High
Advisory: CVE-2022-49696
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49696
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.127, >=5.11.0 <5.15.51, >=5.16.0 <5.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: fix use-after-free Read in tipc_named_reinit

syzbot found the following issue on:
==================================================================
BUG: KASAN: use-after-free in tipc_named_reinit+0x94f/0x9b0
net/tipc/name_distr.c:413
Read of size 8 at addr ffff88805299a000 by task kworker/1:9/23764

CPU: 1 PID: 23764 Comm: kworker/1:9 Not tainted
5.18.0-rc4-syzkaller-00878-g17d49e6e8012 #0
Hardware name: Google Compute Engine/Google Compute Engine,
BIOS Google 01/01/2011
Workqueue: events tipc_net_finalize_work
Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:88 [inline]
 dump_stack_lvl+0xcd/0x134 lib/dump_stack.c:106
 print_address_description.constprop.0.cold+0xeb/0x495
mm/kasan/report.c:313
 print_report mm/kasan/report.c:429 [inline]
 kasan_report.cold+0xf4/0x1c6 mm/kasan/report.c:491
 tipc_named_reinit+0x94f/0x9b0 net/tipc/name_distr.c:413
 tipc_net_finalize+0x234/0x3d0 net/tipc/net.c:138
 process_one_work+0x996/0x1610 kernel/workqueue.c:2289
 worker_thread+0x665/0x1080 kernel/workqueue.c:2436
 kthread+0x2e9/0x3a0 kernel/kthread.c:376
 ret_from_fork+0x1f/0x30 arch/x86/entry/entry_64.S:298
 </TASK>
[...]
==================================================================

In the commit
d966ddcc3821 ("tipc: fix a deadlock when flushing scheduled work"),
the cancel_work_sync() function just to make sure ONLY the work
tipc_net_finalize_work() is executing/pending on any CPU completed before
tipc namespace is destroyed through tipc_exit_net(). But this function
is not guaranteed the work is the last queued. So, the destroyed instance
may be accessed in the work which will try to enqueue later.

In order to completely fix, we re-order the calling of cancel_work_sync()
to make sure the work tipc_net_finalize_work() was last queued and it
must be completed by calling cancel_work_sync().

## References
- https://git.kernel.org/stable/c/361c5521c1e49843b710f455cae3c0a50b714323
- https://git.kernel.org/stable/c/8b246ddd394d7d9640816611693b0096b998e27a
- https://git.kernel.org/stable/c/911600bf5a5e84bfda4d33ee32acc75ecf6159f0
- https://git.kernel.org/stable/c/cd7789e659e84f137631dc1f5ec8d794f2700e6c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49696.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49696
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
