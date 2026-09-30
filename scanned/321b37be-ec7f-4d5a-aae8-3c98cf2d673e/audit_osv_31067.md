# [H] ila: serialize calls to nf_register_net_hooks()

## Summary
Severity: High
Advisory: CVE-2024-57900
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-15
Source: https://osv.dev/vulnerability/CVE-2024-57900
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <5.4.289, >=5.5.0 <5.10.233, >=5.11.0 <5.15.176, >=5.16.0 <6.1.124, >=6.2.0 <6.6.70, >=6.7.0 <6.12.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ila: serialize calls to nf_register_net_hooks()

syzbot found a race in ila_add_mapping() [1]

commit 031ae72825ce ("ila: call nf_unregister_net_hooks() sooner")
attempted to fix a similar issue.

Looking at the syzbot repro, we have concurrent ILA_CMD_ADD commands.

Add a mutex to make sure at most one thread is calling nf_register_net_hooks().

[1]
 BUG: KASAN: slab-use-after-free in rht_key_hashfn include/linux/rhashtable.h:159 [inline]
 BUG: KASAN: slab-use-after-free in __rhashtable_lookup.constprop.0+0x426/0x550 include/linux/rhashtable.h:604
Read of size 4 at addr ffff888028f40008 by task dhcpcd/5501

CPU: 1 UID: 0 PID: 5501 Comm: dhcpcd Not tainted 6.13.0-rc4-syzkaller-00054-gd6ef8b40d075 #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 09/13/2024
Call Trace:
 <IRQ>
  __dump_stack lib/dump_stack.c:94 [inline]
  dump_stack_lvl+0x116/0x1f0 lib/dump_stack.c:120
  print_address_description mm/kasan/report.c:378 [inline]
  print_report+0xc3/0x620 mm/kasan/report.c:489
  kasan_report+0xd9/0x110 mm/kasan/report.c:602
  rht_key_hashfn include/linux/rhashtable.h:159 [inline]
  __rhashtable_lookup.constprop.0+0x426/0x550 include/linux/rhashtable.h:604
  rhashtable_lookup include/linux/rhashtable.h:646 [inline]
  rhashtable_lookup_fast include/linux/rhashtable.h:672 [inline]
  ila_lookup_wildcards net/ipv6/ila/ila_xlat.c:127 [inline]
  ila_xlat_addr net/ipv6/ila/ila_xlat.c:652 [inline]
  ila_nf_input+0x1ee/0x620 net/ipv6/ila/ila_xlat.c:185
  nf_hook_entry_hookfn include/linux/netfilter.h:154 [inline]
  nf_hook_slow+0xbb/0x200 net/netfilter/core.c:626
  nf_hook.constprop.0+0x42e/0x750 include/linux/netfilter.h:269
  NF_HOOK include/linux/netfilter.h:312 [inline]
  ipv6_rcv+0xa4/0x680 net/ipv6/ip6_input.c:309
  __netif_receive_skb_one_core+0x12e/0x1e0 net/core/dev.c:5672
  __netif_receive_skb+0x1d/0x160 net/core/dev.c:5785
  process_backlog+0x443/0x15f0 net/core/dev.c:6117
  __napi_poll.constprop.0+0xb7/0x550 net/core/dev.c:6883
  napi_poll net/core/dev.c:6952 [inline]
  net_rx_action+0xa94/0x1010 net/core/dev.c:7074
  handle_softirqs+0x213/0x8f0 kernel/softirq.c:561
  __do_softirq kernel/softirq.c:595 [inline]
  invoke_softirq kernel/softirq.c:435 [inline]
  __irq_exit_rcu+0x109/0x170 kernel/softirq.c:662
  irq_exit_rcu+0x9/0x30 kernel/softirq.c:678
  instr_sysvec_apic_timer_interrupt arch/x86/kernel/apic/apic.c:1049 [inline]
  sysvec_apic_timer_interrupt+0xa4/0xc0 arch/x86/kernel/apic/apic.c:1049

## References
- https://git.kernel.org/stable/c/1638f430f8900f2375f5de45508fbe553997e190
- https://git.kernel.org/stable/c/17e8fa894345e8d2c7a7642482267b275c3d4553
- https://git.kernel.org/stable/c/260466b576bca0081a7d4acecc8e93687aa22d0e
- https://git.kernel.org/stable/c/3d1b63cf468e446b9feaf4e4e73182b9cc82f460
- https://git.kernel.org/stable/c/ad0677c37c14fa28913daea92d139644d7acf04e
- https://git.kernel.org/stable/c/d3017895e393536b234cf80a83fc463c08a28137
- https://git.kernel.org/stable/c/eba25e21dce7ec70e2b3f121b2f3a25a4ec43eca
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57900.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57900
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
