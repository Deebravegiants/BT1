# [H] ip6: vti: Use ip6_tnl.net in vti6_siocdevprivate().

## Summary
Severity: High
Advisory: CVE-2026-63921
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63921
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.15.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ip6: vti: Use ip6_tnl.net in vti6_siocdevprivate().

After patch 1/2 in this series, vti6_update() unlinks and relinks
the tunnel through t->net. vti6_siocdevprivate() still uses
dev_net(dev) for the collision lookup. For a tunnel moved through
IFLA_NET_NS_FD, dev_net(dev) is the new netns, not t->net.

SIOCCHGTUNNEL on a migrated tunnel then runs:

  net = dev_net(dev)                    /* migrated netns */
  t   = vti6_locate(net, &p1, false)    /* misses target in t->net */
  ...
  t   = netdev_priv(dev)
  vti6_update(t, &p1, false)            /* mutates t->net's hash */

A caller in the migrated netns picks params that match a tunnel
in the creation netns. The lookup in dev_net(dev) finds nothing.
vti6_update() prepends the migrated tunnel at the head of the
creation netns hash bucket for those params. Later lookups in
the creation netns resolve to the migrated device. xfrm receive
delivers the matched packets through a device the caller controls.

Reachable from an unprivileged user namespace (unshare --user
--map-root-user --net). Cross tenant scope on container hosts.

Switch the SIOCCHGTUNNEL path on a non fallback device to use
t->net for the lookup. The lookup now matches the netns
vti6_update() operates on.

Also add ns_capable(self->net->user_ns, CAP_NET_ADMIN) before
the lookup. The check at the top of the case is against
dev_net(dev)->user_ns, which after migration is the attacker's
netns. A caller there can pick params absent from self->net,
the lookup returns NULL, t becomes self, and vti6_update()
inserts the device into the creation netns hash. The new check
requires CAP_NET_ADMIN in the creation netns user_ns too.

SIOCADDTUNNEL and SIOCCHGTUNNEL on the fallback device keep
dev_net(dev), which equals init_net there.

## References
- https://git.kernel.org/stable/c/1acfb7d9c6fc7e209ed7789392697e97e03edd33
- https://git.kernel.org/stable/c/44d2ff7d2178503b93151140a45dfa2ad49c9906
- https://git.kernel.org/stable/c/596f6354c96a891e58c04a09cbfb7b0d1ec00dab
- https://git.kernel.org/stable/c/853f6ea482dfcd3404bbef458ab4d68364eed838
- https://git.kernel.org/stable/c/8b484efd5cb4eeef9021a661e198edc5349dacf6
- https://git.kernel.org/stable/c/94ff740a7f9ef5c010784a325dca00cbf228f941
- https://git.kernel.org/stable/c/d2236348414bdd6558385f35aa7fdc9bf5634011
- https://git.kernel.org/stable/c/df42ac708acc3399bbb6dc5ca16e0540adda7bbf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63921.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63921
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
