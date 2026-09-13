# [C] mptcp: fix a race in mptcp_pm_del_add_timer()

## Summary
Severity: Critical
Advisory: CVE-2025-40257
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2025-40257
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.118, >=6.7.0 <6.12.60, >=6.13.0 <6.17.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: fix a race in mptcp_pm_del_add_timer()

mptcp_pm_del_add_timer() can call sk_stop_timer_sync(sk, &entry->add_timer)
while another might have free entry already, as reported by syzbot.

Add RCU protection to fix this issue.

Also change confusing add_timer variable with stop_timer boolean.

syzbot report:

BUG: KASAN: slab-use-after-free in __timer_delete_sync+0x372/0x3f0 kernel/time/timer.c:1616
Read of size 4 at addr ffff8880311e4150 by task kworker/1:1/44

CPU: 1 UID: 0 PID: 44 Comm: kworker/1:1 Not tainted syzkaller #0 PREEMPT_{RT,(full)}
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 10/02/2025
Workqueue: events mptcp_worker
Call Trace:
 <TASK>
  dump_stack_lvl+0x189/0x250 lib/dump_stack.c:120
  print_address_description mm/kasan/report.c:378 [inline]
  print_report+0xca/0x240 mm/kasan/report.c:482
  kasan_report+0x118/0x150 mm/kasan/report.c:595
  __timer_delete_sync+0x372/0x3f0 kernel/time/timer.c:1616
  sk_stop_timer_sync+0x1b/0x90 net/core/sock.c:3631
  mptcp_pm_del_add_timer+0x283/0x310 net/mptcp/pm.c:362
  mptcp_incoming_options+0x1357/0x1f60 net/mptcp/options.c:1174
  tcp_data_queue+0xca/0x6450 net/ipv4/tcp_input.c:5361
  tcp_rcv_established+0x1335/0x2670 net/ipv4/tcp_input.c:6441
  tcp_v4_do_rcv+0x98b/0xbf0 net/ipv4/tcp_ipv4.c:1931
  tcp_v4_rcv+0x252a/0x2dc0 net/ipv4/tcp_ipv4.c:2374
  ip_protocol_deliver_rcu+0x221/0x440 net/ipv4/ip_input.c:205
  ip_local_deliver_finish+0x3bb/0x6f0 net/ipv4/ip_input.c:239
  NF_HOOK+0x30c/0x3a0 include/linux/netfilter.h:318
  NF_HOOK+0x30c/0x3a0 include/linux/netfilter.h:318
  __netif_receive_skb_one_core net/core/dev.c:6079 [inline]
  __netif_receive_skb+0x143/0x380 net/core/dev.c:6192
  process_backlog+0x31e/0x900 net/core/dev.c:6544
  __napi_poll+0xb6/0x540 net/core/dev.c:7594
  napi_poll net/core/dev.c:7657 [inline]
  net_rx_action+0x5f7/0xda0 net/core/dev.c:7784
  handle_softirqs+0x22f/0x710 kernel/softirq.c:622
  __do_softirq kernel/softirq.c:656 [inline]
  __local_bh_enable_ip+0x1a0/0x2e0 kernel/softirq.c:302
  mptcp_pm_send_ack net/mptcp/pm.c:210 [inline]
 mptcp_pm_addr_send_ack+0x41f/0x500 net/mptcp/pm.c:-1
  mptcp_pm_worker+0x174/0x320 net/mptcp/pm.c:1002
  mptcp_worker+0xd5/0x1170 net/mptcp/protocol.c:2762
  process_one_work kernel/workqueue.c:3263 [inline]
  process_scheduled_works+0xae1/0x17b0 kernel/workqueue.c:3346
  worker_thread+0x8a0/0xda0 kernel/workqueue.c:3427
  kthread+0x711/0x8a0 kernel/kthread.c:463
  ret_from_fork+0x4bc/0x870 arch/x86/kernel/process.c:158
  ret_from_fork_asm+0x1a/0x30 arch/x86/entry/entry_64.S:245
 </TASK>

Allocated by task 44:
  kasan_save_stack mm/kasan/common.c:56 [inline]
  kasan_save_track+0x3e/0x80 mm/kasan/common.c:77
  poison_kmalloc_redzone mm/kasan/common.c:400 [inline]
  __kasan_kmalloc+0x93/0xb0 mm/kasan/common.c:417
  kasan_kmalloc include/linux/kasan.h:262 [inline]
  __kmalloc_cache_noprof+0x1ef/0x6c0 mm/slub.c:5748
  kmalloc_noprof include/linux/slab.h:957 [inline]
  mptcp_pm_alloc_anno_list+0x104/0x460 net/mptcp/pm.c:385
  mptcp_pm_create_subflow_or_signal_addr+0xf9d/0x1360 net/mptcp/pm_kernel.c:355
  mptcp_pm_nl_fully_established net/mptcp/pm_kernel.c:409 [inline]
  __mptcp_pm_kernel_worker+0x417/0x1ef0 net/mptcp/pm_kernel.c:1529
  mptcp_pm_worker+0x1ee/0x320 net/mptcp/pm.c:1008
  mptcp_worker+0xd5/0x1170 net/mptcp/protocol.c:2762
  process_one_work kernel/workqueue.c:3263 [inline]
  process_scheduled_works+0xae1/0x17b0 kernel/workqueue.c:3346
  worker_thread+0x8a0/0xda0 kernel/workqueue.c:3427
  kthread+0x711/0x8a0 kernel/kthread.c:463
  ret_from_fork+0x4bc/0x870 arch/x86/kernel/process.c:158
  ret_from_fork_asm+0x1a/0x30 arch/x86/entry/entry_64.S:245

Freed by task 6630:
  kasan_save_stack mm/kasan/common.c:56 [inline]
  kasan_save_track+0x3e/0x80 mm/kasan/common.c:77
  __kasan_save_free_info+0x46/0x50 mm/kasan/generic.c:587
  kasan_save_free_info mm/kasan/kasan.h:406 [inline]
  poison_slab_object m
---truncated---

## References
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://git.kernel.org/stable/c/385ddc0f008f24d1e7d03be998b3a98a37bd29ff
- https://git.kernel.org/stable/c/426358d9be7ce3518966422f87b96f1bad27295f
- https://git.kernel.org/stable/c/6d3275d4ca62e2c02e1b7e8cd32db59df91c14b7
- https://git.kernel.org/stable/c/9be29f8e7ce4e147e56caac2c3a0ce3573cf9c17
- https://git.kernel.org/stable/c/bbbd75346c8e6490b19c2ba90f38ea66ccf352b2
- https://git.kernel.org/stable/c/c602cc344b4b8d41515fec3ffa98457ac963ee12
- https://git.kernel.org/stable/c/e2d1ad207174a7cd7903dd27a00db4b2dfa6c64b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40257.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40257
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
