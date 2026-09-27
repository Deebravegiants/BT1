# [H] gtp: check skb_pull_data() return in gtp1u_send_echo_resp()

## Summary
Severity: High
Advisory: CVE-2026-64577
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-64577
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

gtp: check skb_pull_data() return in gtp1u_send_echo_resp()

gtp1u_send_echo_resp() ignores skb_pull_data()'s return value. Its
caller gtp1u_udp_encap_recv() only guarantees 16 bytes (udphdr +
gtp1_header), but the pull requests 20 (gtp1_header_long + udphdr). For
a 16-19 byte echo request the pull fails and returns NULL without
advancing skb->data; execution continues, and the following skb_push()
plus the IP header pushed by iptunnel_xmit() move skb->data below
skb->head, tripping skb_under_panic().

Fix it by dropping the packet when skb_pull_data() fails.

  skbuff: skb_under_panic: ...
  kernel BUG at net/core/skbuff.c:214!
  Call Trace:
   skb_push (net/core/skbuff.c:2648)
   iptunnel_xmit (net/ipv4/ip_tunnel_core.c:82)
   gtp_encap_recv (drivers/net/gtp.c:701 drivers/net/gtp.c:808 drivers/net/gtp.c:920)
   udp_queue_rcv_one_skb (net/ipv4/udp.c:2388)
   ...
  Kernel panic - not syncing: Fatal exception in interrupt

## References
- https://git.kernel.org/stable/c/4fc7923871d176ce0e5fecf4a9b7bb915af790ed
- https://git.kernel.org/stable/c/9033fe49926f0e7421fefee922dc086417e905cf
- https://git.kernel.org/stable/c/961e9b1e33445f8e42859ecc020c9f60d8b69a8b
- https://git.kernel.org/stable/c/b3c733eaae7f362601c28ac1533d47a961cd3e1c
- https://git.kernel.org/stable/c/cd170f051dba9ac146fabcd1b91726487c0cb9fa
- https://git.kernel.org/stable/c/cf45d748e437b8dd2dd987f27ee79c8c86f95c88
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64577.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64577
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
