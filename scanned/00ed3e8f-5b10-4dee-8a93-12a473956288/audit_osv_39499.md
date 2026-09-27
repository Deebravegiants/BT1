# [H] bonding: alb: fix UAF in rlb_arp_recv during bond up/down

## Summary
Severity: High
Advisory: CVE-2026-45970
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45970
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.0.0 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

bonding: alb: fix UAF in rlb_arp_recv during bond up/down

The ALB RX path may access rx_hashtbl concurrently with bond
teardown. During rapid bond up/down cycles, rlb_deinitialize()
frees rx_hashtbl while RX handlers are still running, leading
to a null pointer dereference detected by KASAN.

However, the root cause is that rlb_arp_recv() can still be accessed
after setting recv_probe to NULL, which is actually a use-after-free
(UAF) issue. That is the reason for using the referenced commit in the
Fixes tag.

[  214.174138] Oops: general protection fault, probably for non-canonical address 0xdffffc000000001d: 0000 [#1] SMP KASAN PTI
[  214.186478] KASAN: null-ptr-deref in range [0x00000000000000e8-0x00000000000000ef]
[  214.194933] CPU: 30 UID: 0 PID: 2375 Comm: ping Kdump: loaded Not tainted 6.19.0-rc8+ #2 PREEMPT(voluntary)
[  214.205907] Hardware name: Dell Inc. PowerEdge R730/0WCJNT, BIOS 2.14.0 01/14/2022
[  214.214357] RIP: 0010:rlb_arp_recv+0x505/0xab0 [bonding]
[  214.220320] Code: 0f 85 2b 05 00 00 48 b8 00 00 00 00 00 fc ff df 40 0f b6 ed 48 c1 e5 06 49 03 ad 78 01 00 00 48 8d 7d 28 48 89 fa 48 c1 ea 03 <0f> b6
 04 02 84 c0 74 06 0f 8e 12 05 00 00 80 7d 28 00 0f 84 8c 00
[  214.241280] RSP: 0018:ffffc900073d8870 EFLAGS: 00010206
[  214.247116] RAX: dffffc0000000000 RBX: ffff888168556822 RCX: ffff88816855681e
[  214.255082] RDX: 000000000000001d RSI: dffffc0000000000 RDI: 00000000000000e8
[  214.263048] RBP: 00000000000000c0 R08: 0000000000000002 R09: ffffed11192021c8
[  214.271013] R10: ffff8888c9010e43 R11: 0000000000000001 R12: 1ffff92000e7b119
[  214.278978] R13: ffff8888c9010e00 R14: ffff888168556822 R15: ffff888168556810
[  214.286943] FS:  00007f85d2d9cb80(0000) GS:ffff88886ccb3000(0000) knlGS:0000000000000000
[  214.295966] CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
[  214.302380] CR2: 00007f0d047b5e34 CR3: 00000008a1c2e002 CR4: 00000000001726f0
[  214.310347] Call Trace:
[  214.313070]  <IRQ>
[  214.315318]  ? __pfx_rlb_arp_recv+0x10/0x10 [bonding]
[  214.320975]  bond_handle_frame+0x166/0xb60 [bonding]
[  214.326537]  ? __pfx_bond_handle_frame+0x10/0x10 [bonding]
[  214.332680]  __netif_receive_skb_core.constprop.0+0x576/0x2710
[  214.339199]  ? __pfx_arp_process+0x10/0x10
[  214.343775]  ? sched_balance_find_src_group+0x98/0x630
[  214.349513]  ? __pfx___netif_receive_skb_core.constprop.0+0x10/0x10
[  214.356513]  ? arp_rcv+0x307/0x690
[  214.360311]  ? __pfx_arp_rcv+0x10/0x10
[  214.364499]  ? __lock_acquire+0x58c/0xbd0
[  214.368975]  __netif_receive_skb_one_core+0xae/0x1b0
[  214.374518]  ? __pfx___netif_receive_skb_one_core+0x10/0x10
[  214.380743]  ? lock_acquire+0x10b/0x140
[  214.385026]  process_backlog+0x3f1/0x13a0
[  214.389502]  ? process_backlog+0x3aa/0x13a0
[  214.394174]  __napi_poll.constprop.0+0x9f/0x370
[  214.399233]  net_rx_action+0x8c1/0xe60
[  214.403423]  ? __pfx_net_rx_action+0x10/0x10
[  214.408193]  ? lock_acquire.part.0+0xbd/0x260
[  214.413058]  ? sched_clock_cpu+0x6c/0x540
[  214.417540]  ? mark_held_locks+0x40/0x70
[  214.421920]  handle_softirqs+0x1fd/0x860
[  214.426302]  ? __pfx_handle_softirqs+0x10/0x10
[  214.431264]  ? __neigh_event_send+0x2d6/0xf50
[  214.436131]  do_softirq+0xb1/0xf0
[  214.439830]  </IRQ>

The issue is reproducible by repeatedly running
ip link set bond0 up/down while receiving ARP messages, where
rlb_arp_recv() can race with rlb_deinitialize() and dereference
a freed rx_hashtbl entry.

Fix this by setting recv_probe to NULL and then calling
synchronize_net() to wait for any concurrent RX processing to finish.
This ensures that no RX handler can access rx_hashtbl after it is freed
in bond_alb_deinitialize().

## References
- https://git.kernel.org/stable/c/c65cdf46ce340c9c00fbbaf84599d2daff43626e
- https://git.kernel.org/stable/c/d31065526f160ee0244a719230aa069daca2bf4d
- https://git.kernel.org/stable/c/db5435b5342e3aaa4521d0f3ccfe94316b253ca1
- https://git.kernel.org/stable/c/de7c097800f07f3c108185c7a38b53a530ba30ff
- https://git.kernel.org/stable/c/e6834a4c474697df23ab9948fd3577b26bf48656
- https://git.kernel.org/stable/c/f94a0de7b9f32745a14a1621c63087a092823587
- https://git.kernel.org/stable/c/fd54ddc929be1d6c3b3b7b35d6d4642a5d9e803c
- https://git.kernel.org/stable/c/fef13c403be3fb685cb06419e6b3623106aab5ba
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45970.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45970
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
