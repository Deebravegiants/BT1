# [H] ip6_gre: Use cached t->net in ip6erspan_changelink().

## Summary
Severity: High
Advisory: CVE-2026-46120
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46120
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ip6_gre: Use cached t->net in ip6erspan_changelink().

After commit 5e72ce3e3980 ("net: ipv6: Use link netns in newlink() of
rtnl_link_ops"), ip6erspan_newlink() correctly resolves the per-netns
ip6gre hash via link_net. ip6erspan_changelink() was not converted in
that series and still uses dev_net(dev), which diverges from the
device's creation netns after IFLA_NET_NS_FD migration.

This re-inserts the tunnel into the wrong per-netns hash. The
original netns keeps a stale entry. When that netns is later
destroyed, ip6gre_exit_rtnl_net() walks the stale entry, producing a
slab-use-after-free reported by KASAN, followed by a kernel BUG at
net/core/dev.c (LIST_POISON1) in unregister_netdevice_many_notify().

Reachable from an unprivileged user namespace (unshare --user
--map-root-user --net).

ip6gre_changelink() earlier in the same file already uses the cached
t->net; only ip6erspan_changelink() has the wrong shape.

## References
- https://git.kernel.org/stable/c/01b71ff2857d3598337de11e7840a8e3ff21553c
- https://git.kernel.org/stable/c/0fcf6731706f73494245a9c0d64f93bebf95bb51
- https://git.kernel.org/stable/c/1d324c2f43f70c965f25c58cc3611c779adbe47e
- https://git.kernel.org/stable/c/311fdd26eb4443d43b909cc67a10f3a5fd1b21b2
- https://git.kernel.org/stable/c/7bd0f2b162b426b343a114e1b329f0d8d14fdc6e
- https://git.kernel.org/stable/c/cf7fc624329e76c6394653d12353e1d033adea91
- https://git.kernel.org/stable/c/e70cfb40c3a99b232cd42c6a6a10f0d8e039dc82
- https://git.kernel.org/stable/c/eca62bb0569de4d43a4dac06a2092a9d4ca1d702
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46120.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46120
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
