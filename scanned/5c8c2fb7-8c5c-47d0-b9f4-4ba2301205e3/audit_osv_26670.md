# [C] tipc: do not update mtu if msg_max is too small in mtu negotiation

## Summary
Severity: Critical
Advisory: CVE-2023-53517
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2023-53517
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <5.10.181, >=5.11.0 <5.15.113, >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: do not update mtu if msg_max is too small in mtu negotiation

When doing link mtu negotiation, a malicious peer may send Activate msg
with a very small mtu, e.g. 4 in Shuang's testing, without checking for
the minimum mtu, l->mtu will be set to 4 in tipc_link_proto_rcv(), then
n->links[bearer_id].mtu is set to 4294967228, which is a overflow of
'4 - INT_H_SIZE - EMSG_OVERHEAD' in tipc_link_mss().

With tipc_link.mtu = 4, tipc_link_xmit() kept printing the warning:

 tipc: Too large msg, purging xmit list 1 5 0 40 4!
 tipc: Too large msg, purging xmit list 1 15 0 60 4!

And with tipc_link_entry.mtu 4294967228, a huge skb was allocated in
named_distribute(), and when purging it in tipc_link_xmit(), a crash
was even caused:

  general protection fault, probably for non-canonical address 0x2100001011000dd: 0000 [#1] PREEMPT SMP PTI
  CPU: 0 PID: 0 Comm: swapper/0 Kdump: loaded Not tainted 6.3.0.neta #19
  RIP: 0010:kfree_skb_list_reason+0x7e/0x1f0
  Call Trace:
   <IRQ>
   skb_release_data+0xf9/0x1d0
   kfree_skb_reason+0x40/0x100
   tipc_link_xmit+0x57a/0x740 [tipc]
   tipc_node_xmit+0x16c/0x5c0 [tipc]
   tipc_named_node_up+0x27f/0x2c0 [tipc]
   tipc_node_write_unlock+0x149/0x170 [tipc]
   tipc_rcv+0x608/0x740 [tipc]
   tipc_udp_recv+0xdc/0x1f0 [tipc]
   udp_queue_rcv_one_skb+0x33e/0x620
   udp_unicast_rcv_skb.isra.72+0x75/0x90
   __udp4_lib_rcv+0x56d/0xc20
   ip_protocol_deliver_rcu+0x100/0x2d0

This patch fixes it by checking the new mtu against tipc_bearer_min_mtu(),
and not updating mtu if it is too small.

## References
- https://git.kernel.org/stable/c/1dd7ae5e0cf5a56e513f7ab7ab9570b7496281d2
- https://git.kernel.org/stable/c/259683001d7e879fea4b42084fb6560dd9408a7e
- https://git.kernel.org/stable/c/2bd4ff4ffb92113f8acd04dbaed83269172c24b4
- https://git.kernel.org/stable/c/56077b56cd3fb78e1c8619e29581ba25a5c55e86
- https://git.kernel.org/stable/c/575e84d90a74c0b091b3417ba763ebb237aa0a8c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53517.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53517
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
