# [H] ipvlan: Make the addrs_lock be per port

## Summary
Severity: High
Advisory: CVE-2026-23103
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2026-23103
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.10.249, >=5.11.0 <5.15.199, >=5.16.0 <6.1.162, >=6.2.0 <6.6.122, >=6.7.0 <6.12.68, >=6.13.0 <6.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipvlan: Make the addrs_lock be per port

Make the addrs_lock be per port, not per ipvlan dev.

Initial code seems to be written in the assumption,
that any address change must occur under RTNL.
But it is not so for the case of IPv6. So

1) Introduce per-port addrs_lock.

2) It was needed to fix places where it was forgotten
to take lock (ipvlan_open/ipvlan_close)

This appears to be a very minor problem though.
Since it's highly unlikely that ipvlan_add_addr() will
be called on 2 CPU simultaneously. But nevertheless,
this could cause:

1) False-negative of ipvlan_addr_busy(): one interface
iterated through all port->ipvlans + ipvlan->addrs
under some ipvlan spinlock, and another added IP
under its own lock. Though this is only possible
for IPv6, since looks like only ipvlan_addr6_event() can be
called without rtnl_lock.

2) Race since ipvlan_ht_addr_add(port) is called under
different ipvlan->addrs_lock locks

This should not affect performance, since add/remove IP
is a rare situation and spinlock is not taken on fast
paths.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/04ba6de6eff61238e5397c14ac26a6578c7735a5
- https://git.kernel.org/stable/c/1f300c10d92c547c3a7d978e1212ff52f18256ed
- https://git.kernel.org/stable/c/3c149b662cbb202a450e81f938e702ba333864ad
- https://git.kernel.org/stable/c/6a81e2db096913d7e43aada1c350c1282e76db39
- https://git.kernel.org/stable/c/70feb16e3fbfb10b15de1396557c38e99f1ab8df
- https://git.kernel.org/stable/c/88f83e6c9cdb46b8c8ddd0ba01393362963cf589
- https://git.kernel.org/stable/c/d3ba32162488283c0a4c5bedd8817aec91748802
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23103.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23103
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
