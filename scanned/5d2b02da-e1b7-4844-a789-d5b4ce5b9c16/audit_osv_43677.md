# [C] netfilter: nf_conntrack_sip: widen NAT rewrite delta to s32 in sip_help_tcp()

## Summary
Severity: Critical
Advisory: CVE-2026-74569
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74569
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_conntrack_sip: widen NAT rewrite delta to s32 in sip_help_tcp()

sip_help_tcp() stores the size change of each NAT-rewritten SIP message
in s16 diff and accumulates it in s16 tdiff, but a single message can
grow by more than S16_MAX while the packet stays under the 65535
enlarge_skb() limit: nf_nat_sip() rewrites every matching URI, and a long
Contact list expands the message by tens of kilobytes. diff then wraps,
and "datalen = datalen + diff - msglen" yields a huge unsigned datalen,
so the next iteration's ct_sip_get_header() reads past the linearized skb
tail.

Widen diff, tdiff and the seq_adjust hook to s32. Both are bounded by the
65535 byte packet limit, and the seqadj core is already s32
(nf_ct_seqadj_set() takes s32), so no previously accepted input is
rejected.

  BUG: KASAN: use-after-free in ct_sip_get_header (net/netfilter/nf_conntrack_sip.c:464)
  Read of size 1 at addr ffff888010800000 by task ksoftirqd/1/25
   ct_sip_get_header (net/netfilter/nf_conntrack_sip.c:464)
   sip_help_tcp (net/netfilter/nf_conntrack_sip.c:1694)
   nf_confirm (net/netfilter/nf_conntrack_proto.c:183)
   nf_hook_slow (net/netfilter/core.c:619)
   ip6_output (net/ipv6/ip6_output.c:246)
   ip6_forward (net/ipv6/ip6_output.c:690)
   ipv6_rcv (net/ipv6/ip6_input.c:351)
   __netif_receive_skb_one_core (net/core/dev.c:6212)
   process_backlog (net/core/dev.c:6676)
   __napi_poll (net/core/dev.c:7735)
   net_rx_action (net/core/dev.c:7955)
   handle_softirqs (kernel/softirq.c:622)
   run_ksoftirqd (kernel/softirq.c:1076)
   ...

## References
- https://git.kernel.org/stable/c/1b0843f9e9b9b0b9b4b70d143b67e58163c85b2c
- https://git.kernel.org/stable/c/32d4abc8923b0d4046fd63ad6e4917872e44eb6d
- https://git.kernel.org/stable/c/63eea41759fd682229c14e0a2205802b46d106f3
- https://git.kernel.org/stable/c/c97621a110e386b2dd69e276eb699e1d3cec581d
- https://git.kernel.org/stable/c/db3d0e0e5d4bc5ab4fe445b9f413d1b486508ca5
- https://git.kernel.org/stable/c/ed1f9be6dc8e2e280b8725e44ccdc6e0cd38640d
- https://git.kernel.org/stable/c/ef5e2c6555d2bb52dfe0e4053a8c6193f9d83b64
- https://git.kernel.org/stable/c/f74554e67ccf04d1fa71069e8c9afa2717e40716
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74569.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74569
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
