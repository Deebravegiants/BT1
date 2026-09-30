# [H] net: guard timestamp cmsgs to real error queue skbs

## Summary
Severity: High
Advisory: CVE-2026-53223
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53223
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: guard timestamp cmsgs to real error queue skbs

skb_is_err_queue() treats PACKET_OUTGOING as the sole marker for an skb
from sk_error_queue. That assumption is not true for AF_PACKET sockets:
outgoing packet taps are also delivered to packet sockets with
skb->pkt_type == PACKET_OUTGOING, but their skb->cb is owned by AF_PACKET
instead of struct sock_exterr_skb.

If such an skb is received with timestamping enabled, the generic
timestamp cmsg path can read AF_PACKET control-buffer state as
sock_exterr_skb::opt_stats. With SO_RXQ_OVFL enabled, the packet drop
counter overlaps opt_stats. An odd drop count makes the path emit
SCM_TIMESTAMPING_OPT_STATS with skb->len and skb->data. For non-linear
skbs this copies past the linear head and can trigger hardened usercopy or
disclose adjacent heap contents.

Keep skb_is_err_queue() local to net/socket.c, but make it verify that
the PACKET_OUTGOING marker is paired with the sock_rmem_free destructor
installed by sock_queue_err_skb(). AF_PACKET receive skbs use normal
receive ownership and no longer pass as error-queue skbs, while legitimate
sk_error_queue entries keep the PACKET_OUTGOING marker and sock_rmem_free
ownership.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/1ee90b77b727df903033db873c75caac5c27ec98
- https://git.kernel.org/stable/c/24a0d548d3a765cd4558224e4f8e06e14cba26e3
- https://git.kernel.org/stable/c/3dde4fb941fa5649ab809f6cd3e20e0c424a4e31
- https://git.kernel.org/stable/c/71ff5cdd5da61d0438e902aa0fd68c28bc901abe
- https://git.kernel.org/stable/c/ad9a0374ee6d11048e1f74cd5180bad58b9848b4
- https://git.kernel.org/stable/c/b903e9b5629ec8dd6db92174070045bf81ad7060
- https://git.kernel.org/stable/c/e0665b2a8e90bb08bd205062c75662b502d31797
- https://git.kernel.org/stable/c/eb51a9ad3ceb01bc6c0fb608dbc856e03ee6f24a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53223.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53223
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
