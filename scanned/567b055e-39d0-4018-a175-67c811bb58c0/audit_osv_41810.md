# [H] ip6: vti: Use ip6_tnl.net in vti6_changelink().

## Summary
Severity: High
Advisory: CVE-2026-63917
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63917
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.15.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ip6: vti: Use ip6_tnl.net in vti6_changelink().

ip netns add ns1
ip netns add ns2
ip -n ns1 link add vti6_test type vti6 remote ::1 local ::2 key 7
ip -n ns1 link set vti6_test netns ns2
ip -n ns2 link set vti6_test type vti6 remote ::3 local ::4 key 9
ip netns del ns2
ip netns del ns1
[  132.495484] ------------[ cut here ]------------
[  132.497609] kernel BUG at net/core/dev.c:12376!

Commit 61220ab34948 ("vti6: Enable namespace changing") dropped
NETIF_F_NETNS_LOCAL from vti6 devices. A vti6 tunnel can then
move through IFLA_NET_NS_FD. After the move dev_net(dev) points
at the new netns while t->net stays at the creation netns.

vti6_changelink() and vti6_update() still use dev_net(dev) and
dev_net(t->dev). They unlink from one per netns hash and relink
into another. The creation netns is left with a stale entry.
cleanup_net() of that netns later walks freed memory.

Reachable from an unprivileged user namespace (unshare --user
--map-root-user --net). Cross tenant scope on container hosts.

## References
- https://git.kernel.org/stable/c/0cdce7618464f7fb06f461e8f4ad575cb1d570f4
- https://git.kernel.org/stable/c/11b326fb0a374f4654f9be22d0f0f7abd9f7d3fe
- https://git.kernel.org/stable/c/225b467e3b631f38be22e4b38062a1fed02fdd21
- https://git.kernel.org/stable/c/d9c5eecdb3c740e65038651db7c686b10d76d1bc
- https://git.kernel.org/stable/c/ee1778ba0f5cb53be771f97017d01eb356c797bf
- https://git.kernel.org/stable/c/f1e89a943ee574d0f2f16246eb3f2d7330fdeb03
- https://git.kernel.org/stable/c/f5c68875e25f331e497ddfbe81e2d8163a87f136
- https://git.kernel.org/stable/c/fc32be9ac2788524c6b24efd681cce7a6e731a92
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63917.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63917
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
