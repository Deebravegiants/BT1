# [C] ila: reload IPv6 header after pskb_may_pull in checksum adjust

## Summary
Severity: Critical
Advisory: CVE-2026-68127
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68127
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ila: reload IPv6 header after pskb_may_pull in checksum adjust

ila_csum_adjust_transport() caches ip6h = ipv6_hdr(skb) before calling
pskb_may_pull(). On a non-linear skb whose transport header sits in a page
fragment, pskb_may_pull() can call __pskb_pull_tail() / pskb_expand_head()
and free the old skb head, leaving ip6h dangling; the following
get_csum_diff(ip6h, p) then reads freed memory. ila_update_ipv6_locator()
uses ip6h (and the iaddr derived from it) again after the csum-adjust
call and additionally writes the new locator through that pointer.

Impact: a remote IPv6 packet routed through a configured ILA
csum-adjust-transport route or receive-side mapping triggers a
slab-use-after-free in ila_update_ipv6_locator() (KASAN). The route or
mapping requires CAP_NET_ADMIN to configure, but trigger packets are
unauthenticated once it exists.

Reload ip6h after each pskb_may_pull() in ila_csum_adjust_transport()
before the csum-diff read. In ila_update_ipv6_locator() only the
ILA_CSUM_ADJUST_TRANSPORT case pulls the skb, so reload ip6h and iaddr in
that case alone before the destination-address write; the neutral-map
modes never pull and keep their cached pointers.

## References
- https://git.kernel.org/stable/c/1eadcb43893b897ade85ac5bf5c618054bc3c655
- https://git.kernel.org/stable/c/472aba2603ca74c4f7722cb0c0296942b0776b8d
- https://git.kernel.org/stable/c/7097a0280b178237265681be66d1bef11d15894b
- https://git.kernel.org/stable/c/896a9512d0d83c2a4b357e5585b7b62a8e3f95c1
- https://git.kernel.org/stable/c/92d3817649df2b0b6a008a686c8275c88d7ef594
- https://git.kernel.org/stable/c/ba353caafb06ccee57b78d3254e3cebf1dea4a93
- https://git.kernel.org/stable/c/c6a13ae00dab3a1a8c7cf2f843f0fc9e8d4b0ccc
- https://git.kernel.org/stable/c/e451a904606c571f731ef7a06b3398619dce5300
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68127.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68127
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
