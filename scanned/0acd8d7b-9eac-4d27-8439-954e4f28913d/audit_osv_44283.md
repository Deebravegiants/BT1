# [C] net: gro: properly validate BIG TCP aggregation criteria

## Summary
Severity: Critical
Advisory: CVE-2026-80725
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-29
Source: https://osv.dev/vulnerability/CVE-2026-80725
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.185, >=6.2.0 <6.6.154, >=6.7.0 <6.12.106, >=6.13.0 <6.18.47

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: gro: properly validate BIG TCP aggregation criteria

When GRO attempts to aggregate packets beyond GRO_LEGACY_MAX_SIZE (64KB),
BIG TCP should only be permitted for plain IPv4 TCP and plain IPv6 TCP
(with sufficient MAC header room to insert the temporary HBH jumbo header).

However, commit b1a78b9b9886 ("net: add support for ipv4 big tcp")
loosened the check in skb_gro_receive(), leading to several issues:

1. skb_gro_receive() checked skb_headroom(p) instead of the actual space
   before the MAC header (p->mac_header). Because skb_headroom(p) includes
   mac_len, crafted frames (e.g. injected via AF_PACKET) can pass the check
   with p->mac_header < 8 bytes. When ipv6_gro_complete() inserts the
   temporary HBH jumbo header, the memmove() starts before skb->head,
   causing an out-of-bounds write and wrapping skb->mac_header.
2. It allowed non-IP protocols such as software VLAN (ETH_P_8021Q /
   ETH_P_8021AD) to aggregate beyond 64KB because
   p->protocol != ETH_P_IPV6 was true.
3. It checked p->encapsulation instead of NAPI_GRO_CB(skb)->encap_mark,
   allowing encapsulated flows (e.g. SIT / IPv6-in-IPv4) to aggregate
   beyond 64KB.

Fix skb_gro_receive() to strictly enforce:
- NAPI_GRO_CB(skb)->proto == IPPROTO_TCP
- Not encapsulated (!NAPI_GRO_CB(skb)->encap_mark && !p->encapsulation)
- Protocol must be either ETH_P_IP or ETH_P_IPV6
- If ETH_P_IPV6, p->mac_header must be at least
  sizeof(struct hop_jumbo_hdr)

Returning -E2BIG from skb_gro_receive() ensures that packets which cannot
become BIG TCP are cleanly flushed at <= 64KB and delivered intact without
dropping.

This issue does not exist in mainline (7.0+) because the subsystem was
rewritten in commit 81be30c1f5f2 ("net/ipv6: Drop HBH for BIG TCP on RX
side"), making this fix relevant only for older stable branches like
6.18.y.

## References
- https://git.kernel.org/stable/c/03cb8cc2961f5f781d12e903782cb3815ed84b1c
- https://git.kernel.org/stable/c/37a5dcd6837fc2afc44a7bc3ed8af4e983783d46
- https://git.kernel.org/stable/c/3ce832e2bd431d0c12ba525ed73ad8fbc4191da5
- https://git.kernel.org/stable/c/81be30c1f5f2bffda1f04c0efd0746af10b9643a
- https://git.kernel.org/stable/c/e907bf694ed55bdfe421be99dba35751a655df25
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80725.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80725
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
