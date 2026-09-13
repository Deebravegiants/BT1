# [C] net: gro: fix double aggregation of flush-marked skbs

## Summary
Severity: Critical
Advisory: CVE-2026-68136
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68136
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.266, >=5.11.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: gro: fix double aggregation of flush-marked skbs

Commit 0ab03f353d36 ("net-gro: Fix GRO flush when receiving a GSO
packet.") added a flush check to skb_gro_receive(), but
skb_gro_receive_list() lacks the same validation.

As a result, packets marked with NAPI_GRO_CB(skb)->flush may still be
re-aggregated.

This allows already-GRO'd packets with existing frag_list to be
re-aggregated into a new GRO session, corrupting the frag_list chain
structure. When skb_segment() attempts to unpack these malformed packets,
it encounters invalid state and triggers a kernel panic.

Scenario (Tethering/Device forwarding):
  1. Driver: Generated aggregated packet P1 via LRO with frag_list
  2. Dev A: Receives aggregated fraglist packet and flush flag set
  3. Dev A: Re-enters GRO, skb_gro_receive_list() is called
  4. Missing flush check allows re-aggregation despite flush flag
  5. Frag_list chain becomes corrupted (loops or dangling refs)
  6. Dev B: TX path calls skb_segment(), crashes on corrupted frag_list

Root cause in skb_segment():
  The check at line ~4891:
    if (hsize <= 0 && i >= nfrags && skb_headlen(list_skb) &&
        (skb_headlen(list_skb) == len || sg)) {

  When frag_list is corrupted by double aggregation, when list_skb is
  a NULL pointer from skb->next, skb_headlen(list_skb) dereference
  NULL/corrupted pointers occurs.

Call Trace:
 skb_headlen(NULL skb)
 skb_segment
 tcp_gso_segment
 tcp4_gso_segment
 inet_gso_segment
 skb_mac_gso_segment
 __skb_gso_segment
 skb_gso_segment
 validate_xmit_skb
 validate_xmit_skb_list
 sch_direct_xmit
 qdisc_restart
 __qdisc_run
 qdisc_run
 net_tx_action

Fix: Add NAPI_GRO_CB(skb)->flush validation to the early-return check in
skb_gro_receive_list(), matching the defensive programming pattern of
skb_gro_receive().

## References
- https://git.kernel.org/stable/c/107e1a469f53a2a70874f3f12bf6fcd23925da1d
- https://git.kernel.org/stable/c/7fc7e35212cf58c134310fb47566a844297ceae9
- https://git.kernel.org/stable/c/a4dfd46cc8f08a29c6183794790547d0945f3d45
- https://git.kernel.org/stable/c/d1fb23f8f794ac4683127bd49a6422bd87e0ac02
- https://git.kernel.org/stable/c/db3e82da616f52e2b27e25e7be3fde2f2a5e54d6
- https://git.kernel.org/stable/c/e751256486d0ded20f5a9f9863467f1dce65142f
- https://git.kernel.org/stable/c/fc0c0f7a207f0cd2d2aa725696c907f7d03af9e0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68136.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68136
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
