# [H] xfrm: reject optional IPTFS templates in outbound policies

## Summary
Severity: High
Advisory: CVE-2026-68420
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68420
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: reject optional IPTFS templates in outbound policies

syzbot reported a stack-out-of-bounds read in xfrm_state_find()
which flows from xfrm_tmpl_resolve_one().

Commit 3d776e31c841 ("xfrm: Reject optional tunnel/BEET mode
templates in outbound policies") disallowed optional tunnel and
BEET in outbound policies to prevent this. Later when IPTFS
added, it was not covered by that fix and can still trigger
the out-of-bounds read;

Extend the check to disallow optional IPTFS in outbound policies
as well. IPTFS should be identical to tunnel mode.
IN and FWD policies are not affected: xfrm_tmpl_resolve_one()
is only reachable via the outbound path.

Reproducer, before:

ip link add dummy0 type dummy
ip link set dummy0 up
ip addr add 10.1.1.1/24 dev dummy0
ip xfrm policy add src 10.1.1.1/32 dst 10.1.1.2/32 dir out tmpl
  src fc00::dead:1 dst fc00::dead:2 proto esp reqid 1 mode iptfs
  level use tmpl src fc00::dead:1 dst fc00::dead:2 proto esp reqid
  2 mode transport
ping -W 1 -c 1 10.1.1.2
PING 10.1.1.2 (10.1.1.2) 56(84) bytes of data.

[   64.168420] ==================================================================
[   64.169977] BUG: KASAN: stack-out-of-bounds in __xfrm6_addr_hash+0x11e/0x170
[   64.169977] Read of size 4 at addr ffff88800e1ffd20 by task ping/2844

[   64.169977] CPU: 2 UID: 0 PID: 2844 Comm: ping Not tainted 7.1.0-rc7-00180-geb23b588430a #98 PREEMPT(full)
[   64.169977] Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.16.3-debian-1.16.3-2 04/01/2014
[   64.169977] Call Trace:
[   64.169977]  <TASK>
[   64.169977]  dump_stack_lvl+0x47/0x70
[   64.169977]  ? __xfrm6_addr_hash+0x11e/0x170
[   64.169977]  print_report+0x152/0x4b0
[   64.169977]  ? ksys_mmap_pgoff+0x6d/0xa0
[   64.169977]  ? entry_SYSCALL_64_after_hwframe+0x76/0x7e
[   64.169977]  ? rcu_read_unlock_sched+0xa/0x20
[   64.169977]  ? __virt_addr_valid+0x21b/0x230
[   64.169977]  ? __xfrm6_addr_hash+0x11e/0x170
[   64.169977]  kasan_report+0xa8/0xd0
[   64.169977]  ? __xfrm6_addr_hash+0x11e/0x170
[   64.169977]  __xfrm6_addr_hash+0x11e/0x170
[   64.169977]  __xfrm_dst_hash+0x24/0xc0
[   64.169977]  xfrm_state_find+0xa2d/0x2f90
[   64.169977]  ? __pfx_xfrm_state_find+0x10/0x10
[   64.169977]  ? __pfx_ftrace_graph_ret_addr+0x10/0x10
[   64.169977]  ? __pfx_ftrace_graph_ret_addr+0x10/0x10
[   64.169977]  xfrm_tmpl_resolve_one+0x210/0x570
[   64.169977]  ? __pfx_xfrm_tmpl_resolve_one+0x10/0x10
[   64.169977]  ? __pfx_stack_trace_consume_entry+0x10/0x10
[   64.169977]  ? kernel_text_address+0x5b/0x80
[   64.169977]  ? __kernel_text_address+0xe/0x30
[   64.169977]  ? unwind_get_return_address+0x5e/0x90
[   64.169977]  ? arch_stack_walk+0x8c/0xe0
[   64.169977]  xfrm_tmpl_resolve+0x130/0x200
[   64.169977]  ? __pfx_xfrm_tmpl_resolve+0x10/0x10
[   64.169977]  ? __pfx_xfrm_policy_inexact_lookup_rcu+0x10/0x10
[   64.169977]  ? __refcount_add_not_zero.constprop.0+0xb2/0x110
[   64.169977]  ? __pfx___refcount_add_not_zero.constprop.0+0x10/0x10
[   64.169977]  xfrm_resolve_and_create_bundle+0xd5/0x310
[   64.169977]  ? __pfx_xfrm_resolve_and_create_bundle+0x10/0x10
[   64.169977]  ? __pfx_xfrm_policy_lookup_bytype+0x10/0x10
[   64.169977]  ? __pfx_xfrm_policy_lookup_bytype+0x10/0x10
[   64.169977]  xfrm_lookup_with_ifid+0x3d8/0xb80
[   64.169977]  ? __pfx_xfrm_lookup_with_ifid+0x10/0x10
[   64.169977]  ? ip_route_output_key_hash+0xc6/0x110
[   64.169977]  ? kasan_save_track+0x10/0x30
[   64.169977]  xfrm_lookup_route+0x18/0xe0
[   64.169977]  ip4_datagram_release_cb+0x4c9/0x530
[   64.169977]  ? __pfx_ip4_datagram_release_cb+0x10/0x10
[   64.169977]  ? do_raw_spin_lock+0x71/0xc0
[   64.169977]  ? __pfx_do_raw_spin_lock+0x10/0x10
[   64.169977]  release_sock+0xb0/0x170
[   64.169977]  udp_connect+0x43/0x50
[   64.169977]  __sys_connect+0xa6/0x100
[   64.169977]  ? alloc_fd+0x2e9/0x300
[   64.169977]  ? __pfx___sys_connect+0x10/0x10
[   64.169977]  ? preempt_latency
---truncated---

## References
- https://git.kernel.org/stable/c/9333f4b6f44858fc98eb12bf26b8d2959eb975d5
- https://git.kernel.org/stable/c/d7fc6f351c478586980a521d63b0214d9c055e78
- https://git.kernel.org/stable/c/ea528f18231ec0f33317be57f8866913b19aba6e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68420.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68420
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
