# [C] net: lwtunnel: Drop skb metadata before LWT encapsulation

## Summary
Severity: Critical
Advisory: CVE-2026-80612
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80612
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: lwtunnel: Drop skb metadata before LWT encapsulation

skb metadata is meant for passing information between XDP and TC. It lives
in the skb headroom, immediately before skb->data. LWT programs cannot
access the __sk_buff->data_meta pseudo-pointer to metadata.

However, LWT encapsulation prepends outer headers, moving skb->data back
over the headroom where the metadata sits. On an RX-originated (forwarded)
packet that still carries XDP metadata this goes wrong in two different
ways, depending on the encap type:

1. Non-BPF LWT encaps (mpls, seg6, ioam6 ...) call skb_push()/skb_pull()
   and silently overwrite the metadata that sits in the headroom.

2) BPF LWT xmit calls bpf_skb_change_head(), which uses skb_data_move().
   That helper expects metadata immediately before skb->data. But since
   the IP output path runs LWT xmit before neighbour output has built
   the outgoing L2 header, for forwarded packets skb->data points at the
   L3 header while skb_mac_header() still points at the old L2 header.
   skb_data_move() sees metadata ending at skb_mac_header(), not before
   skb->data, warns and clears metadata:

  WARNING: CPU: 21 PID: 454557 at include/linux/skbuff.h:4609 skb_data_move+0x47/0x90
  CPU: 21 UID: 0 PID: 454557 Comm: napi/iconduit-g Tainted: G           O        6.18.21 #1
  RIP: 0010:skb_data_move+0x47/0x90
  Call Trace:
   <IRQ>
   bpf_skb_change_head+0xe6/0x1a0
   bpf_prog_...+0x213/0x2e3
   run_lwt_bpf.isra.0+0x1d3/0x360
   bpf_xmit+0x46/0xe0
   lwtunnel_xmit+0xa1/0xf0
   ip_finish_output2+0x1e7/0x5e0
   ip_output+0x63/0x100
   __netif_receive_skb_one_core+0x85/0xa0
   process_backlog+0x9c/0x150
   __napi_poll+0x2b/0x190
   net_rx_action+0x40b/0x7f0
   handle_softirqs+0xd2/0x270
   do_softirq+0x3f/0x60
   </IRQ>

That is what happens, as for how to fix it - a received packet that
carries metadata can reach an encap through any of the three LWT
redirect modes:

  LWTUNNEL_STATE_INPUT_REDIRECT
   ip6_rcv_finish
     dst_input
       lwtunnel_input

  LWTUNNEL_STATE_OUTPUT_REDIRECT
   ip6_rcv_finish
     dst_input
       ip6_forward
         ip6_forward_finish
           dst_output
             lwtunnel_output

  LWTUNNEL_STATE_XMIT_REDIRECT
   ip6_rcv_finish
     dst_input
       ip6_forward
         ip6_forward_finish
           dst_output
             ip6_output
               ip6_finish_output
                 ip6_finish_output2
                   lwtunnel_xmit

Every encap funnels through the three LWT dispatch helpers, so drop the
metadata there, right before handing the skb to the encap op. This
single chokepoint covers all encap types and all three redirect modes:

  - lwtunnel_input():  seg6, rpl, ila, seg6_local
  - lwtunnel_output(): ioam6
  - lwtunnel_xmit():   mpls, LWT BPF xmit

Alternatively, we could clear the metadata right after TC ingress hook.
That would require a compromise, however. Metadata would become
inaccessible from TC egress (in setups where it actually reaches the
hook it tact, that is without any L2 tunnels on path).

## References
- https://git.kernel.org/stable/c/19eec11f3ab5dd29ba58f5f209c24e946c95ef12
- https://git.kernel.org/stable/c/c00320b0e355c4bf0ae4743a53b4180fea237546
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80612.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80612
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
