# [H] netfilter: nf_nat: avoid invalid nat_net pointer use on failed nf_nat_init()

## Summary
Severity: High
Advisory: CVE-2026-72419
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72419
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_nat: avoid invalid nat_net pointer use on failed nf_nat_init()

We ran into below KASAN splat, which is mostly uninteresting, beside
for having nf_nat_register_fn() in the call chain as a cause for the
offending access:

==================================================================
BUG: KASAN: slab-out-of-bounds in nf_nat_register_fn+0x5f9/0x640
Read of size 8 at addr ffff890031e54c20 by task iptables/9510

CPU: 0 UID: 0 PID: 9510 Comm: iptables Not tainted 6.18.18-grsec-full-20260320181326 #1 PREEMPT(voluntary)
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.16.3-debian-1.16.3-2 04/01/2014
Call Trace:
 <TASK>
 […] dump_stack_lvl+0xee/0x160 ffff88004117eeb8
 […] print_report+0x6e/0x640 ffff88004117eee0
 […] ? __phys_addr+0x8e/0x140 ffff88004117eef0
 […] ? kasan_addr_to_slab+0x51/0xe0 ffff88004117ef08
 […] ? complete_report_info+0xec/0x1c0 ffff88004117ef20
 […] ? nf_nat_register_fn+0x5f9/0x640 ffff88004117ef48
 […] kasan_report+0xbc/0x140 ffff88004117ef50
 […] ? nf_nat_register_fn+0x5f9/0x640 ffff88004117ef90
 […] nf_nat_register_fn+0x5f9/0x640 ffff88004117eff8
 […] ? nf_nat_icmp_reply_translation+0x6e0/0x6e0 ffff88004117f070
 […] nf_tables_register_hook.part.0+0xa0/0x220 ffff88004117f080
 […] nf_tables_addchain.constprop.0+0x1054/0x1fc0 ffff88004117f0b8
 […] ? nft_chain_lookup.part.0+0x4ce/0xac0 ffff88004117f130
 […] ? nf_tables_abort+0x3d80/0x3d80 ffff88004117f190
 […] ? nf_tables_dumpreset_obj+0x100/0x100 ffff88004117f1c8
 […] ? nft_table_lookup.part.0+0x255/0x300 ffff88004117f310
 […] ? nf_tables_newchain+0x21a4/0x2fa0 ffff88004117f358
 […] nf_tables_newchain+0x21a4/0x2fa0 ffff88004117f360
 […] ? nf_tables_addchain.constprop.0+0x1fc0/0x1fc0 ffff88004117f458
 […] ? nla_get_range_signed+0x4a0/0x4a0 ffff88004117f488
 […] ? lock_acquire+0x16f/0x320 ffff88004117f490
 […] ? find_held_lock+0x3b/0xe0 ffff88004117f4b0
 […] ? __nla_parse+0x45/0x80 ffff88004117f500
 […] nfnetlink_rcv_batch+0xbca/0x19a0 ffff88004117f550
 […] ? nfnetlink_net_exit_batch+0x120/0x120 ffff88004117f618
 […] ? __sanitizer_cov_trace_switch+0x63/0xe0 ffff88004117f720
 […] ? gr_acl_handle_mmap+0x1c4/0x320 ffff88004117f7c0
 […] ? nla_get_range_signed+0x4a0/0x4a0 ffff88004117f7e8
 […] ? gr_is_capable+0x6f/0xe0 ffff88004117f830
 […] ? __nla_parse+0x45/0x80 ffff88004117f860
 […] ? skb_pull+0x103/0x1a0 ffff88004117f880
 […] nfnetlink_rcv+0x3db/0x4a0 ffff88004117f8b0
 […] ? nfnetlink_rcv_batch+0x19a0/0x19a0 ffff88004117f8d8
 […] ? netlink_lookup+0xe2/0x240 ffff88004117f900
 […] netlink_unicast+0x74b/0xb00 ffff88004117f930
 […] ? netlink_attachskb+0xb20/0xb20 ffff88004117f980
 […] ? __check_object_size+0x3e/0xaa0 ffff88004117f998
 […] ? security_netlink_send+0x51/0x160 ffff88004117f9c8
 […] netlink_sendmsg+0xa03/0x1200 ffff88004117f9f8
 […] ? netlink_unicast+0xb00/0xb00 ffff88004117fa70
 […] ? netlink_unicast+0xb00/0xb00 ffff88004117fac8
 […] ? ____sys_sendmsg+0xe2a/0x1040 ffff88004117faf8
 […] ____sys_sendmsg+0xe2a/0x1040 ffff88004117fb00
 […] ? kernel_recvmsg+0x300/0x300 ffff88004117fb60
 […] ? reacquire_held_locks+0xe9/0x260 ffff88004117fbc8
 […] ___sys_sendmsg+0x138/0x200 ffff88004117fbf8
 […] ? do_recvmmsg+0x7e0/0x7e0 ffff88004117fc30
 […] ? lockdep_hardirqs_on_prepare+0x101/0x1e0 ffff88004117fc50
 […] ? lock_acquire+0x16f/0x320 ffff88004117fd20
 […] ? lock_acquire+0x16f/0x320 ffff88004117fd58
 […] ? find_held_lock+0x3b/0xe0 ffff88004117fd70
 […] __sys_sendmsg+0x17a/0x260 ffff88004117fdc8
 […] ? __sys_sendmsg_sock+0x80/0x80 ffff88004117fdf0
 […] ? syscall_trace_enter+0x15e/0x2c0 ffff88004117fe98
 […] do_syscall_64+0x7d/0x400 ffff88004117fec8
 […] entry_SYSCALL_64_safe_stack+0x4a/0x60 ffff88004117fef8
 </TASK>
==================================================================

The out-of-bounds report, though, is a red herring as it is f
---truncated---

## References
- https://git.kernel.org/stable/c/069cfe3de2a5e16069485893cd04665ab769c1d8
- https://git.kernel.org/stable/c/359d8ff97362a4662356104540e4814bff9dad7c
- https://git.kernel.org/stable/c/87f7a720de2545fdac29c85acb7163676feacdaf
- https://git.kernel.org/stable/c/a73e7ac3f3b69e9581ec7bfd889ff3e9b8c773f7
- https://git.kernel.org/stable/c/e794f633021defcfa98e17d73b955cd07590831f
- https://git.kernel.org/stable/c/eb14aba91163c33d8c99f9d7c06690e08b56a250
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72419.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72419
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
