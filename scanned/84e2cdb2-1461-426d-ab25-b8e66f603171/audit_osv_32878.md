# [H] net: clear the dst when changing skb protocol

## Summary
Severity: High
Advisory: CVE-2025-38192
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-38192
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.15.209, >=5.16.0 <6.1.167, >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: clear the dst when changing skb protocol

A not-so-careful NAT46 BPF program can crash the kernel
if it indiscriminately flips ingress packets from v4 to v6:

  BUG: kernel NULL pointer dereference, address: 0000000000000000
    ip6_rcv_core (net/ipv6/ip6_input.c:190:20)
    ipv6_rcv (net/ipv6/ip6_input.c:306:8)
    process_backlog (net/core/dev.c:6186:4)
    napi_poll (net/core/dev.c:6906:9)
    net_rx_action (net/core/dev.c:7028:13)
    do_softirq (kernel/softirq.c:462:3)
    netif_rx (net/core/dev.c:5326:3)
    dev_loopback_xmit (net/core/dev.c:4015:2)
    ip_mc_finish_output (net/ipv4/ip_output.c:363:8)
    NF_HOOK (./include/linux/netfilter.h:314:9)
    ip_mc_output (net/ipv4/ip_output.c:400:5)
    dst_output (./include/net/dst.h:459:9)
    ip_local_out (net/ipv4/ip_output.c:130:9)
    ip_send_skb (net/ipv4/ip_output.c:1496:8)
    udp_send_skb (net/ipv4/udp.c:1040:8)
    udp_sendmsg (net/ipv4/udp.c:1328:10)

The output interface has a 4->6 program attached at ingress.
We try to loop the multicast skb back to the sending socket.
Ingress BPF runs as part of netif_rx(), pushes a valid v6 hdr
and changes skb->protocol to v6. We enter ip6_rcv_core which
tries to use skb_dst(). But the dst is still an IPv4 one left
after IPv4 mcast output.

Clear the dst in all BPF helpers which change the protocol.
Try to preserve metadata dsts, those may carry non-routing
metadata.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/2a3ad42a57b43145839f2f233fb562247658a6d9
- https://git.kernel.org/stable/c/98b1d8dc9a3170b2614f1e8c93854e75cdd83980
- https://git.kernel.org/stable/c/a046f183d21ab5ace5a96ece4cf9873a42f003a7
- https://git.kernel.org/stable/c/ba9db6f907ac02215e30128770f85fbd7db2fcf9
- https://git.kernel.org/stable/c/bfa4d86e130a09f67607482e988313430e38f6c4
- https://git.kernel.org/stable/c/e9994e7b9f7bbb882d13c8191731649249150d21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38192.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38192
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
