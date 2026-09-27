# [M] ip6mr: Fix skb_under_panic in ip6mr_cache_report()

## Summary
Severity: Medium
Advisory: CVE-2023-53365
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2023-53365
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.26 <4.14.322, >=4.15.0 <4.19.291, >=4.20.0 <5.4.253, >=5.5.0 <5.10.190, >=5.11.0 <5.15.126, >=5.16.0 <6.1.45, >=6.2.0 <6.4.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ip6mr: Fix skb_under_panic in ip6mr_cache_report()

skbuff: skb_under_panic: text:ffffffff88771f69 len:56 put:-4
 head:ffff88805f86a800 data:ffff887f5f86a850 tail:0x88 end:0x2c0 dev:pim6reg
 ------------[ cut here ]------------
 kernel BUG at net/core/skbuff.c:192!
 invalid opcode: 0000 [#1] PREEMPT SMP KASAN
 CPU: 2 PID: 22968 Comm: kworker/2:11 Not tainted 6.5.0-rc3-00044-g0a8db05b571a #236
 Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.15.0-1 04/01/2014
 Workqueue: ipv6_addrconf addrconf_dad_work
 RIP: 0010:skb_panic+0x152/0x1d0
 Call Trace:
  <TASK>
  skb_push+0xc4/0xe0
  ip6mr_cache_report+0xd69/0x19b0
  reg_vif_xmit+0x406/0x690
  dev_hard_start_xmit+0x17e/0x6e0
  __dev_queue_xmit+0x2d6a/0x3d20
  vlan_dev_hard_start_xmit+0x3ab/0x5c0
  dev_hard_start_xmit+0x17e/0x6e0
  __dev_queue_xmit+0x2d6a/0x3d20
  neigh_connected_output+0x3ed/0x570
  ip6_finish_output2+0x5b5/0x1950
  ip6_finish_output+0x693/0x11c0
  ip6_output+0x24b/0x880
  NF_HOOK.constprop.0+0xfd/0x530
  ndisc_send_skb+0x9db/0x1400
  ndisc_send_rs+0x12a/0x6c0
  addrconf_dad_completed+0x3c9/0xea0
  addrconf_dad_work+0x849/0x1420
  process_one_work+0xa22/0x16e0
  worker_thread+0x679/0x10c0
  ret_from_fork+0x28/0x60
  ret_from_fork_asm+0x11/0x20

When setup a vlan device on dev pim6reg, DAD ns packet may sent on reg_vif_xmit().
reg_vif_xmit()
    ip6mr_cache_report()
        skb_push(skb, -skb_network_offset(pkt));//skb_network_offset(pkt) is 4
And skb_push declared as:
	void *skb_push(struct sk_buff *skb, unsigned int len);
		skb->data -= len;
		//0xffff88805f86a84c - 0xfffffffc = 0xffff887f5f86a850
skb->data is set to 0xffff887f5f86a850, which is invalid mem addr, lead to skb_push() fails.

## References
- https://git.kernel.org/stable/c/0438e60a00d4e335b3c36397dbf26c74b5d13ef0
- https://git.kernel.org/stable/c/1683124129a4263dd5bce2475bab110e95fa0346
- https://git.kernel.org/stable/c/1bb54a21f4d9b88442f8c3307c780e2db64417e4
- https://git.kernel.org/stable/c/30e0191b16e8a58e4620fa3e2839ddc7b9d4281c
- https://git.kernel.org/stable/c/3326c711f18d18fe6e1f5d83d3a7eab07e5a1560
- https://git.kernel.org/stable/c/691a09eecad97e745b9aa0e3918db46d020bdacb
- https://git.kernel.org/stable/c/8382e7ed2d63e6c2daf6881fa091526dc6c879cd
- https://git.kernel.org/stable/c/a96d74d1076c82a4cef02c150d9996b21354c78d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53365.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53365
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
