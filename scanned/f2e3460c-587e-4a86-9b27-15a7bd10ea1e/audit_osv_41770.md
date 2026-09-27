# [H] net: ip_gre: require CAP_NET_ADMIN in the device netns for changelink

## Summary
Severity: High
Advisory: CVE-2026-63829
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63829
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ip_gre: require CAP_NET_ADMIN in the device netns for changelink

A tunnel changelink() operates on at most two netns, dev_net(dev) and
the tunnel link netns t->net. They differ once the device is created in
or moved to a netns other than the one the request runs in. The rtnl
changelink path checks CAP_NET_ADMIN only against dev_net(dev), so a
caller privileged there but not in t->net can rewrite a tunnel that
lives in t->net.

Add rtnl_dev_link_net_capable() next to rtnl_get_net_ns_capable() in
net/core/rtnetlink.c. It requires CAP_NET_ADMIN in the link netns and is
skipped when the link netns is dev_net(dev), where the rtnl path already
checked it. The other patches in this series use the same helper.

Gate ipgre_changelink() and erspan_changelink() with it, at the top of
the op before any attribute is parsed, because the parsers update live
tunnel fields first. ipgre_netlink_parms() sets t->collect_md before
ip_tunnel_changelink() runs.

Commit 8b484efd5cb4 ("ip6: vti: Use ip6_tnl.net in
vti6_siocdevprivate().") added the same check on the ioctl path. This
adds it on RTM_NEWLINK.

## References
- https://git.kernel.org/stable/c/1697957eb0971d420dde42862b88eb43506a1105
- https://git.kernel.org/stable/c/19275943d8fe903eb7b9aa53e380e41efd042ada
- https://git.kernel.org/stable/c/47b5d3d506609b08b2e1f7c14f0b681a1953d572
- https://git.kernel.org/stable/c/8165f7ff57d9667d2bb477ef6af83ede7fed4ad7
- https://git.kernel.org/stable/c/866b0f5ae599490bd496fd84581c68ac8b94e6af
- https://git.kernel.org/stable/c/92b766fc55156e0da2ecd0c2302c971118f8a229
- https://git.kernel.org/stable/c/9831bc9ecb402957810c2045c663fbfe9b09e296
- https://git.kernel.org/stable/c/e54c05ed3d9c28733fb9e5837219aca3691defa3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63829.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63829
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
