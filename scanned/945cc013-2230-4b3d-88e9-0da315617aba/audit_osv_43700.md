# [C] ip6_tunnel: clear skb2->cb[] in ip6ip6_err()

## Summary
Severity: Critical
Advisory: CVE-2026-74597
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74597
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ip6_tunnel: clear skb2->cb[] in ip6ip6_err()

ip6ip6_err() clones an outer IPv6 ICMP error skb, pulls it to the
quoted inner IPv6 packet, and then passes the clone to icmpv6_send().
The clone still carries the outer packet's inet6_skb_parm in skb->cb.

If the outer packet had a Home Address Option, IP6CB(skb2)->dsthao
remains non-zero after skb_pull(). icmpv6_send() later calls
mip6_addr_swap(), which uses that stale dsthao offset against the quoted
inner packet. A malformed inner destination-options header can then make
the HAO lookup and address swap run past the end of the quoted packet
and corrupt skb_shared_info.

Clear skb2->cb[] before pulling the quoted inner IPv6 packet so the
reply path does not reuse metadata left by the outer IPv6 stack.

## References
- https://git.kernel.org/stable/c/0dadb0620ab65949a8bc2439dd28ea3c942fe87d
- https://git.kernel.org/stable/c/44fe898df302e91c5ee5acbc71ffa74e78e6c183
- https://git.kernel.org/stable/c/484134e1eb07d700a73b1e4bbf3fb503e299be60
- https://git.kernel.org/stable/c/4eb15c465337b18f44716c499cd6ad63eee0ad54
- https://git.kernel.org/stable/c/64e41736a26f37ab6215bc2e6df125df05aceb08
- https://git.kernel.org/stable/c/b6816536a2990c0db44a26130a03e40b441e829b
- https://git.kernel.org/stable/c/f803c086399da277b5d0ff36a107d0f162751800
- https://git.kernel.org/stable/c/fbf40faa0414b753212494ad197542002e66ed9e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74597.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74597
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
