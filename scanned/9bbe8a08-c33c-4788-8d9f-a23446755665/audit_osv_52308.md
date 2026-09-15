# [H] CVE-2021-47309

## Summary
Severity: High
Advisory: CVE-2021-47309
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47309
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: validate lwtstate->data before returning from skb_tunnel_info()

skb_tunnel_info() returns pointer of lwtstate->data as ip_tunnel_info
type without validation. lwtstate->data can have various types such as
mpls_iptunnel_encap, etc and these are not compatible.
So skb_tunnel_info() should validate before returning that pointer.

Splat looks like:
BUG: KASAN: slab-out-of-bounds in vxlan_get_route+0x418/0x4b0 [vxlan]
Read of size 2 at addr ffff888106ec2698 by task ping/811

CPU: 1 PID: 811 Comm: ping Not tainted 5.13.0+ #1195
Call Trace:
 dump_stack_lvl+0x56/0x7b
 print_address_description.constprop.8.cold.13+0x13/0x2ee
 ? vxlan_get_route+0x418/0x4b0 [vxlan]
 ? vxlan_get_route+0x418/0x4b0 [vxlan]
 kasan_report.cold.14+0x83/0xdf
 ? vxlan_get_route+0x418/0x4b0 [vxlan]
 vxlan_get_route+0x418/0x4b0 [vxlan]
 [ ... ]
 vxlan_xmit_one+0x148b/0x32b0 [vxlan]
 [ ... ]
 vxlan_xmit+0x25c5/0x4780 [vxlan]
 [ ... ]
 dev_hard_start_xmit+0x1ae/0x6e0
 __dev_queue_xmit+0x1f39/0x31a0
 [ ... ]
 neigh_xmit+0x2f9/0x940
 mpls_xmit+0x911/0x1600 [mpls_iptunnel]
 lwtunnel_xmit+0x18f/0x450
 ip_finish_output2+0x867/0x2040
 [ ... ]

## References
- https://git.kernel.org/stable/c/8bb1589c89e61e3b182dd546f1021928ebb5c2a6
- https://git.kernel.org/stable/c/a915379594f1e045421635c6316d8f3ffa018c58
- https://git.kernel.org/stable/c/b61d327cd3cc5ea591f3bf751dd11e034f388bb5
- https://git.kernel.org/stable/c/e7f3c9df40515a6c6b46f36c4c94cf48a043f887
- https://git.kernel.org/stable/c/2179d96ec702cc33ead02a9ce40ece599b8538c5
- https://git.kernel.org/stable/c/67a9c94317402b826fc3db32afc8f39336803d97
- https://git.kernel.org/stable/c/83bdcfbd968bcc91a0632b7b625e4a9b0cba5e0d
- https://git.kernel.org/stable/c/8aa13a86964cdec4fd969ef677c6614ff068641a
