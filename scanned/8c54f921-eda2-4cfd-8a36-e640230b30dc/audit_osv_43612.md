# [C] vxlan: use pskb_network_may_pull() in route_shortcircuit()

## Summary
Severity: Critical
Advisory: CVE-2026-74473
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74473
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

vxlan: use pskb_network_may_pull() in route_shortcircuit()

route_shortcircuit() currently calls pskb_may_pull(skb, sizeof(struct iphdr))
(or ipv6hdr), which checks if bytes are available starting from skb->data.

However, in vxlan_xmit(), skb->data points to the MAC header, so
skb_network_offset(skb) is ETH_HLEN (14 bytes). Using pskb_may_pull(skb, 20)
only checks 20 bytes from skb->data (which is 14 bytes MAC header + 6 bytes of
IP header), leaving the rest of the IP header potentially un-pulled in non-linear
frags. Subsequent dereferences of ip_hdr(skb)->daddr can read beyond the pulled
linear buffer length.

Fix this by using pskb_network_may_pull(), which adds skb_network_offset(skb) to
the length check to ensure the full network header is present in the linear buffer.

## References
- https://git.kernel.org/stable/c/214ba43faf106cb06cd3dd30999c5c809c868b53
- https://git.kernel.org/stable/c/26bb2dd0a8839617e2c79ffbbe1923f8e4bab9fb
- https://git.kernel.org/stable/c/42887be7c4cf283cce02cd0fb6411221167c8b6c
- https://git.kernel.org/stable/c/4f3f96e771a20263635bb5e1307c112d613b4bbd
- https://git.kernel.org/stable/c/6bd0a3a1b5744166946f0c551a6665c3b46b05e4
- https://git.kernel.org/stable/c/aa0d31376d574ac858a40078431a77127bf04ee4
- https://git.kernel.org/stable/c/c419af4924c1593500a40519730ed98575d04a3e
- https://git.kernel.org/stable/c/ee799977d7941dbfb11049e17edd9eaf4f8820f7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74473.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74473
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
