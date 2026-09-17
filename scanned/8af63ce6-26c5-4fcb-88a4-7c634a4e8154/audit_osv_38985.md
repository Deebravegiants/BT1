# [H] ovpn: tcp - fix packet extraction from stream

## Summary
Severity: High
Advisory: CVE-2026-43254
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43254
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ovpn: tcp - fix packet extraction from stream

When processing TCP stream data in ovpn_tcp_recv, we receive large
cloned skbs from __strp_rcv that may contain multiple coalesced packets.
The current implementation has two bugs:

1. Header offset overflow: Using pskb_pull with large offsets on
   coalesced skbs causes skb->data - skb->head to exceed the u16 storage
   of skb->network_header. This causes skb_reset_network_header to fail
   on the inner decapsulated packet, resulting in packet drops.

2. Unaligned protocol headers: Extracting packets from arbitrary
   positions within the coalesced TCP stream provides no alignment
   guarantees for the packet data causing performance penalties on
   architectures without efficient unaligned access. Additionally,
   openvpn's 2-byte length prefix on TCP packets causes the subsequent
   4-byte opcode and packet ID fields to be inherently misaligned.

Fix both issues by allocating a new skb for each openvpn packet and
using skb_copy_bits to extract only the packet content into the new
buffer, skipping the 2-byte length prefix. Also, check the length before
invoking the function that performs the allocation to avoid creating an
invalid skb.

If the packet has to be forwarded to userspace the 2-byte prefix can be
pushed to the head safely, without misalignment.

As a side effect, this approach also avoids the expensive linearization
that pskb_pull triggers on cloned skbs with page fragments. In testing,
this resulted in TCP throughput improvements of up to 74%.

## References
- https://git.kernel.org/stable/c/0315bec883c67fa1413c61e504a28dc5bd02eb37
- https://git.kernel.org/stable/c/7dba6cd7fb168d7615194a631c9c100c1c224131
- https://git.kernel.org/stable/c/d4f687fbbce45b5e88438e89b5e26c0c15847992
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43254.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43254
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
