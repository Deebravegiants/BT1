# [H] net: gso: Forbid IPv6 TSO with extensions on devices with only IPV6_CSUM

## Summary
Severity: High
Advisory: CVE-2025-39770
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-11
Source: https://osv.dev/vulnerability/CVE-2025-39770
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.44, >=6.12.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: gso: Forbid IPv6 TSO with extensions on devices with only IPV6_CSUM

When performing Generic Segmentation Offload (GSO) on an IPv6 packet that
contains extension headers, the kernel incorrectly requests checksum offload
if the egress device only advertises NETIF_F_IPV6_CSUM feature, which has
a strict contract: it supports checksum offload only for plain TCP or UDP
over IPv6 and explicitly does not support packets with extension headers.
The current GSO logic violates this contract by failing to disable the feature
for packets with extension headers, such as those used in GREoIPv6 tunnels.

This violation results in the device being asked to perform an operation
it cannot support, leading to a `skb_warn_bad_offload` warning and a collapse
of network throughput. While device TSO/USO is correctly bypassed in favor
of software GSO for these packets, the GSO stack must be explicitly told not
to request checksum offload.

Mask NETIF_F_IPV6_CSUM, NETIF_F_TSO6 and NETIF_F_GSO_UDP_L4
in gso_features_check if the IPv6 header contains extension headers to compute
checksum in software.

The exception is a BIG TCP extension, which, as stated in commit
68e068cabd2c6c53 ("net: reenable NETIF_F_IPV6_CSUM offload for BIG TCP packets"):
"The feature is only enabled on devices that support BIG TCP TSO.
The header is only present for PF_PACKET taps like tcpdump,
and not transmitted by physical devices."

kernel log output (truncated):
WARNING: CPU: 1 PID: 5273 at net/core/dev.c:3535 skb_warn_bad_offload+0x81/0x140
...
Call Trace:
 <TASK>
 skb_checksum_help+0x12a/0x1f0
 validate_xmit_skb+0x1a3/0x2d0
 validate_xmit_skb_list+0x4f/0x80
 sch_direct_xmit+0x1a2/0x380
 __dev_xmit_skb+0x242/0x670
 __dev_queue_xmit+0x3fc/0x7f0
 ip6_finish_output2+0x25e/0x5d0
 ip6_finish_output+0x1fc/0x3f0
 ip6_tnl_xmit+0x608/0xc00 [ip6_tunnel]
 ip6gre_tunnel_xmit+0x1c0/0x390 [ip6_gre]
 dev_hard_start_xmit+0x63/0x1c0
 __dev_queue_xmit+0x6d0/0x7f0
 ip6_finish_output2+0x214/0x5d0
 ip6_finish_output+0x1fc/0x3f0
 ip6_xmit+0x2ca/0x6f0
 ip6_finish_output+0x1fc/0x3f0
 ip6_xmit+0x2ca/0x6f0
 inet6_csk_xmit+0xeb/0x150
 __tcp_transmit_skb+0x555/0xa80
 tcp_write_xmit+0x32a/0xe90
 tcp_sendmsg_locked+0x437/0x1110
 tcp_sendmsg+0x2f/0x50
...
skb linear:   00000000: e4 3d 1a 7d ec 30 e4 3d 1a 7e 5d 90 86 dd 60 0e
skb linear:   00000010: 00 0a 1b 34 3c 40 20 11 00 00 00 00 00 00 00 00
skb linear:   00000020: 00 00 00 00 00 12 20 11 00 00 00 00 00 00 00 00
skb linear:   00000030: 00 00 00 00 00 11 2f 00 04 01 04 01 01 00 00 00
skb linear:   00000040: 86 dd 60 0e 00 0a 1b 00 06 40 20 23 00 00 00 00
skb linear:   00000050: 00 00 00 00 00 00 00 00 00 12 20 23 00 00 00 00
skb linear:   00000060: 00 00 00 00 00 00 00 00 00 11 bf 96 14 51 13 f9
skb linear:   00000070: ae 27 a0 a8 2b e3 80 18 00 40 5b 6f 00 00 01 01
skb linear:   00000080: 08 0a 42 d4 50 d5 4b 70 f8 1a

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/041e2f945f82fdbd6fff577b79c33469430297aa
- https://git.kernel.org/stable/c/2156d9e9f2e483c8c3906c0ea57ea312c1424235
- https://git.kernel.org/stable/c/794ddbb7b63b6828c75967b9bcd43b086716e7a1
- https://git.kernel.org/stable/c/864e3396976ef41de6cc7bc366276bf4e084fff2
- https://git.kernel.org/stable/c/a0478d7e888028f85fa7785ea838ce0ca09398e2
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39770.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39770
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
