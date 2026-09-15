# [H] ovpn: fix possible use-after-free in ovpn_net_xmit

## Summary
Severity: High
Advisory: CVE-2026-45929
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45929
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ovpn: fix possible use-after-free in ovpn_net_xmit

When building the skb_list in ovpn_net_xmit, skb_share_check will free
the original skb if it is shared. The current implementation continues
to use the stale skb pointer for subsequent operations:
- peer lookup,
- skb_dst_drop (even though all segments produced by skb_gso_segment
  will have a dst attached),
- ovpn_peer_stats_increment_tx.

Fix this by moving the peer lookup and skb_dst_drop before segmentation
so that the original skb is still valid when used. Return early if all
segments fail skb_share_check and the list ends up empty.
Also switch ovpn_peer_stats_increment_tx to use skb_list.next; the next
patch fixes the stats logic.

## References
- https://git.kernel.org/stable/c/3e4fbcb4e078915367ba5576cd70d76dbc970f95
- https://git.kernel.org/stable/c/442915c96a9bff1c7080e2aedabb1c03faa28d81
- https://git.kernel.org/stable/c/a5ec7baa44ea3a1d6aa0ca31c0ad82edf9affe41
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45929.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45929
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
