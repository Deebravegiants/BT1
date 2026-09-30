# [H] flow_dissector: check device type before reading ETH_ADDRS

## Summary
Severity: High
Advisory: CVE-2026-72444
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72444
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

flow_dissector: check device type before reading ETH_ADDRS

__skb_flow_dissect() unconditionally reads 12 bytes from eth_hdr(skb)
when FLOW_DISSECTOR_KEY_ETH_ADDRS is requested. This assumes the skb
has a valid Ethernet header at mac_header, which is not always the case.

The problem can be triggered by:
 1. Creating a TUN device in L3 mode (IFF_TUN, hard_header_len=0)
 2. Attaching a multiq qdisc with a flower filter matching on eth_src
 3. Sending a packet through AF_PACKET

Since TUN in L3 mode has no link-layer header, mac_header points to
the L3 data area. The flow dissector reads 12 bytes of uninitialized
skb memory, which then propagates through fl_set_masked_key() and is
used as a rhashtable lookup key in __fl_lookup(), as reported by KMSAN.

Rejecting the filter in the control path (at tc filter add time) is
not feasible because TC filter blocks can be shared between arbitrary
devices -- a filter installed on an Ethernet device may later classify
packets on a headerless device through a shared block. The device
association is not fixed at filter creation time.

Fix this by gating the memcpy on dev->type == ARPHRD_ETHER, which
ensures only true Ethernet-framed packets have their addresses read.
This is more precise than the previous hard_header_len >= 12 check,
which would incorrectly pass for non-Ethernet link types like IPoIB
(ARPHRD_INFINIBAND, hard_header_len=24) and FDDI (hard_header_len=21)
whose L2 headers are not in Ethernet format. Additionally check
skb_mac_header_was_set() to guard against the pathological case where
mac_header is the unset sentinel (~0U), which would cause eth_hdr() to
return a wild pointer.

For the act_mirred redirect case (Ethernet packet redirected to a
non-Ethernet device sharing a TC block), zeroing the key is the correct
behavior: the packet is now being classified on the target device, where
Ethernet address matching is not semantically meaningful.

Note: on non-Ethernet devices, the zeroed key will match a filter
configured with all-zero MAC addresses. This is an improvement over the
previous behavior where uninitialized memory could randomly match any
filter.

## References
- https://git.kernel.org/stable/c/0fe6455b8e1a22414f39c07bc90a1df12b52ec74
- https://git.kernel.org/stable/c/594c90b197141944f25991b8314de5c26ee27a7e
- https://git.kernel.org/stable/c/825de39f0c35a112148799b3cbe45af3766c018a
- https://git.kernel.org/stable/c/9a65860959db594dfc1820c7fdc09285fb7556bf
- https://git.kernel.org/stable/c/bf6e8af2c8be77489bedeae9f8a9654cb710e500
- https://git.kernel.org/stable/c/c6d3bcb0f934d4297ac5fa1c8656ae40694fb601
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72444.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72444
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
