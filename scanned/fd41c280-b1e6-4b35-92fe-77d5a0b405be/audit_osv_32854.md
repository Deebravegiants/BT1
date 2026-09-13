# [C] net: openvswitch: Fix the dead loop of MPLS parse

## Summary
Severity: Critical
Advisory: CVE-2025-38146
Ecosystem: Linux
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38146
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.94, >=6.7.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: openvswitch: Fix the dead loop of MPLS parse

The unexpected MPLS packet may not end with the bottom label stack.
When there are many stacks, The label count value has wrapped around.
A dead loop occurs, soft lockup/CPU stuck finally.

stack backtrace:
UBSAN: array-index-out-of-bounds in /build/linux-0Pa0xK/linux-5.15.0/net/openvswitch/flow.c:662:26
index -1 is out of range for type '__be32 [3]'
CPU: 34 PID: 0 Comm: swapper/34 Kdump: loaded Tainted: G           OE   5.15.0-121-generic #131-Ubuntu
Hardware name: Dell Inc. PowerEdge C6420/0JP9TF, BIOS 2.12.2 07/14/2021
Call Trace:
 <IRQ>
 show_stack+0x52/0x5c
 dump_stack_lvl+0x4a/0x63
 dump_stack+0x10/0x16
 ubsan_epilogue+0x9/0x36
 __ubsan_handle_out_of_bounds.cold+0x44/0x49
 key_extract_l3l4+0x82a/0x840 [openvswitch]
 ? kfree_skbmem+0x52/0xa0
 key_extract+0x9c/0x2b0 [openvswitch]
 ovs_flow_key_extract+0x124/0x350 [openvswitch]
 ovs_vport_receive+0x61/0xd0 [openvswitch]
 ? kernel_init_free_pages.part.0+0x4a/0x70
 ? get_page_from_freelist+0x353/0x540
 netdev_port_receive+0xc4/0x180 [openvswitch]
 ? netdev_port_receive+0x180/0x180 [openvswitch]
 netdev_frame_hook+0x1f/0x40 [openvswitch]
 __netif_receive_skb_core.constprop.0+0x23a/0xf00
 __netif_receive_skb_list_core+0xfa/0x240
 netif_receive_skb_list_internal+0x18e/0x2a0
 napi_complete_done+0x7a/0x1c0
 bnxt_poll+0x155/0x1c0 [bnxt_en]
 __napi_poll+0x30/0x180
 net_rx_action+0x126/0x280
 ? bnxt_msix+0x67/0x80 [bnxt_en]
 handle_softirqs+0xda/0x2d0
 irq_exit_rcu+0x96/0xc0
 common_interrupt+0x8e/0xa0
 </IRQ>

## References
- https://git.kernel.org/stable/c/0bdc924bfb319fb10d1113cbf091fc26fb7b1f99
- https://git.kernel.org/stable/c/3c1906a3d50cb94fd0a10e97a1c0a40c0f033cb7
- https://git.kernel.org/stable/c/4b9a086eedc1fddae632310386098c12155e3d0a
- https://git.kernel.org/stable/c/69541e58323ec3e3904e1fa87a6213961b1f52f4
- https://git.kernel.org/stable/c/8ebcd311b4866ab911d1445ead08690e67f0c488
- https://git.kernel.org/stable/c/ad17eb86d042d72a59fd184ad1adf34f5eb36843
- https://git.kernel.org/stable/c/f26fe7c3002516dd3c288f1012786df31f4d89e0
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38146.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38146
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
