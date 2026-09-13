# [H] macvlan: fix error recovery in macvlan_common_newlink()

## Summary
Severity: High
Advisory: CVE-2026-23209
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-14
Source: https://osv.dev/vulnerability/CVE-2026-23209
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.10.250, >=5.11.0 <5.15.200, >=5.16.0 <6.1.163, >=6.2.0 <6.6.124, >=6.7.0 <6.12.70, >=6.13.0 <6.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

macvlan: fix error recovery in macvlan_common_newlink()

valis provided a nice repro to crash the kernel:

ip link add p1 type veth peer p2
ip link set address 00:00:00:00:00:20 dev p1
ip link set up dev p1
ip link set up dev p2

ip link add mv0 link p2 type macvlan mode source
ip link add invalid% link p2 type macvlan mode source macaddr add 00:00:00:00:00:20

ping -c1 -I p1 1.2.3.4

He also gave a very detailed analysis:

<quote valis>

The issue is triggered when a new macvlan link is created  with
MACVLAN_MODE_SOURCE mode and MACVLAN_MACADDR_ADD (or
MACVLAN_MACADDR_SET) parameter, lower device already has a macvlan
port and register_netdevice() called from macvlan_common_newlink()
fails (e.g. because of the invalid link name).

In this case macvlan_hash_add_source is called from
macvlan_change_sources() / macvlan_common_newlink():

This adds a reference to vlan to the port's vlan_source_hash using
macvlan_source_entry.

vlan is a pointer to the priv data of the link that is being created.

When register_netdevice() fails, the error is returned from
macvlan_newlink() to rtnl_newlink_create():

        if (ops->newlink)
                err = ops->newlink(dev, &params, extack);
        else
                err = register_netdevice(dev);
        if (err < 0) {
                free_netdev(dev);
                goto out;
        }

and free_netdev() is called, causing a kvfree() on the struct
net_device that is still referenced in the source entry attached to
the lower device's macvlan port.

Now all packets sent on the macvlan port with a matching source mac
address will trigger a use-after-free in macvlan_forward_source().

</quote valis>

With all that, my fix is to make sure we call macvlan_flush_sources()
regardless of @create value whenever "goto destroy_macvlan_port;"
path is taken.

Many thanks to valis for following up on this issue.

## References
- https://git.kernel.org/stable/c/11ba9f0dc865136174cb98834280fb21bbc950c7
- https://git.kernel.org/stable/c/5dae6b36a7cb7a4fcf4121b95e9ca7f96f816c8a
- https://git.kernel.org/stable/c/986967a162142710076782d5b93daab93a892980
- https://git.kernel.org/stable/c/c43d0e787cbba569ec9d11579ed370b50fab6c9c
- https://git.kernel.org/stable/c/cdedcd5aa3f3cb8b7ae0f87ab3a936d0bd583d66
- https://git.kernel.org/stable/c/da5c6b8ae47e414be47e5e04def15b25d5c962dc
- https://git.kernel.org/stable/c/f8db6475a83649689c087a8f52486fcc53e627e9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23209.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23209
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
