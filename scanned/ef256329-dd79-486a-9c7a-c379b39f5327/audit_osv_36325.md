# [H] dst: fix races in rt6_uncached_list_del() and rt_del_uncached_list()

## Summary
Severity: High
Advisory: CVE-2026-23004
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-25
Source: https://osv.dev/vulnerability/CVE-2026-23004
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.6.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

dst: fix races in rt6_uncached_list_del() and rt_del_uncached_list()

syzbot was able to crash the kernel in rt6_uncached_list_flush_dev()
in an interesting way [1]

Crash happens in list_del_init()/INIT_LIST_HEAD() while writing
list->prev, while the prior write on list->next went well.

static inline void INIT_LIST_HEAD(struct list_head *list)
{
	WRITE_ONCE(list->next, list); // This went well
	WRITE_ONCE(list->prev, list); // Crash, @list has been freed.
}

Issue here is that rt6_uncached_list_del() did not attempt to lock
ul->lock, as list_empty(&rt->dst.rt_uncached) returned
true because the WRITE_ONCE(list->next, list) happened on the other CPU.

We might use list_del_init_careful() and list_empty_careful(),
or make sure rt6_uncached_list_del() always grabs the spinlock
whenever rt->dst.rt_uncached_list has been set.

A similar fix is neeed for IPv4.

[1]

 BUG: KASAN: slab-use-after-free in INIT_LIST_HEAD include/linux/list.h:46 [inline]
 BUG: KASAN: slab-use-after-free in list_del_init include/linux/list.h:296 [inline]
 BUG: KASAN: slab-use-after-free in rt6_uncached_list_flush_dev net/ipv6/route.c:191 [inline]
 BUG: KASAN: slab-use-after-free in rt6_disable_ip+0x633/0x730 net/ipv6/route.c:5020
Write of size 8 at addr ffff8880294cfa78 by task kworker/u8:14/3450

CPU: 0 UID: 0 PID: 3450 Comm: kworker/u8:14 Tainted: G             L      syzkaller #0 PREEMPT_{RT,(full)}
Tainted: [L]=SOFTLOCKUP
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 10/25/2025
Workqueue: netns cleanup_net
Call Trace:
 <TASK>
  dump_stack_lvl+0xe8/0x150 lib/dump_stack.c:120
  print_address_description mm/kasan/report.c:378 [inline]
  print_report+0xca/0x240 mm/kasan/report.c:482
  kasan_report+0x118/0x150 mm/kasan/report.c:595
  INIT_LIST_HEAD include/linux/list.h:46 [inline]
  list_del_init include/linux/list.h:296 [inline]
  rt6_uncached_list_flush_dev net/ipv6/route.c:191 [inline]
  rt6_disable_ip+0x633/0x730 net/ipv6/route.c:5020
  addrconf_ifdown+0x143/0x18a0 net/ipv6/addrconf.c:3853
 addrconf_notify+0x1bc/0x1050 net/ipv6/addrconf.c:-1
  notifier_call_chain+0x19d/0x3a0 kernel/notifier.c:85
  call_netdevice_notifiers_extack net/core/dev.c:2268 [inline]
  call_netdevice_notifiers net/core/dev.c:2282 [inline]
  netif_close_many+0x29c/0x410 net/core/dev.c:1785
  unregister_netdevice_many_notify+0xb50/0x2330 net/core/dev.c:12353
  ops_exit_rtnl_list net/core/net_namespace.c:187 [inline]
  ops_undo_list+0x3dc/0x990 net/core/net_namespace.c:248
  cleanup_net+0x4de/0x7b0 net/core/net_namespace.c:696
  process_one_work kernel/workqueue.c:3257 [inline]
  process_scheduled_works+0xad1/0x1770 kernel/workqueue.c:3340
  worker_thread+0x8a0/0xda0 kernel/workqueue.c:3421
  kthread+0x711/0x8a0 kernel/kthread.c:463
  ret_from_fork+0x510/0xa50 arch/x86/kernel/process.c:158
  ret_from_fork_asm+0x1a/0x30 arch/x86/entry/entry_64.S:246
 </TASK>

Allocated by task 803:
  kasan_save_stack mm/kasan/common.c:57 [inline]
  kasan_save_track+0x3e/0x80 mm/kasan/common.c:78
  unpoison_slab_object mm/kasan/common.c:340 [inline]
  __kasan_slab_alloc+0x6c/0x80 mm/kasan/common.c:366
  kasan_slab_alloc include/linux/kasan.h:253 [inline]
  slab_post_alloc_hook mm/slub.c:4953 [inline]
  slab_alloc_node mm/slub.c:5263 [inline]
  kmem_cache_alloc_noprof+0x18d/0x6c0 mm/slub.c:5270
  dst_alloc+0x105/0x170 net/core/dst.c:89
  ip6_dst_alloc net/ipv6/route.c:342 [inline]
  icmp6_dst_alloc+0x75/0x460 net/ipv6/route.c:3333
  mld_sendpack+0x683/0xe60 net/ipv6/mcast.c:1844
  mld_send_cr net/ipv6/mcast.c:2154 [inline]
  mld_ifc_work+0x83e/0xd60 net/ipv6/mcast.c:2693
  process_one_work kernel/workqueue.c:3257 [inline]
  process_scheduled_works+0xad1/0x1770 kernel/workqueue.c:3340
  worker_thread+0x8a0/0xda0 kernel/workqueue.c:3421
  kthread+0x711/0x8a0 kernel/kthread.c:463
  ret_from_fork+0x510/0xa50 arch/x86/kernel/process.c:158
  ret_from_fork_asm+0x1a/0x30 arch/x86/entry/entr
---truncated---

## References
- https://git.kernel.org/stable/c/722de945216144af7cd4d39bdeb936108d2595a7
- https://git.kernel.org/stable/c/815db2363e51f0ef416947492d4dac5b7a520f56
- https://git.kernel.org/stable/c/9a6f0c4d5796ab89b5a28a890ce542344d58bd69
- https://git.kernel.org/stable/c/f24a52948c95e02facbca2b3b6eb5a225e27eb01
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23004.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23004
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
