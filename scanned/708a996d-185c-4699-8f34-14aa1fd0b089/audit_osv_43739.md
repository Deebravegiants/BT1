# [H] ipv4: fix use-after-free in fib_nhc_update_mtu()

## Summary
Severity: High
Advisory: CVE-2026-74656
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74656
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv4: fix use-after-free in fib_nhc_update_mtu()

fib_nhc_update_mtu() walks the nexthop exception table under RTNL, but
RTNL does not serialize this walk with PMTU exception updates. The walk
uses rcu_dereference_protected() with a constant true condition without
holding fnhe_lock.

The following interleaving can therefore occur:

  CPU 0                              CPU 1
  fib_nhc_update_mtu()               update_or_create_fnhe()
    load fnhe                          spin_lock_bh(&fnhe_lock)
                                       fnhe_remove_oldest()
                                         unlink fnhe
                                         kfree_rcu(fnhe, rcu)
    <quiescent state>
    access fnhe after grace period

KASAN reported:

  BUG: KASAN: slab-use-after-free in fib_nhc_update_mtu+0x3df/0x410
  Read of size 8 at addr ffff888107d49000 by task poc/90
  Call Trace:
   fib_nhc_update_mtu+0x3df/0x410
   fib_sync_mtu+0x7a/0xd0
   fib_netdev_event+0x229/0x3f0
   netif_set_mtu_ext+0x33a/0x570
   dev_set_mtu+0x88/0x120

The same walk updates fnhe_pmtu and fnhe_mtu_locked. These fields form a
pair and other writers serialize them with fnhe_lock. RCU alone prevents
reclamation, but would still allow concurrent writers to leave a mixed
pair.

Walk the table under RCU and acquire fnhe_lock only while updating each
exception. RCU keeps the current entry alive while the short critical
section serializes its paired PMTU fields. This avoids holding the global
lock while scanning all 2048 buckets for every nexthop.

## References
- https://git.kernel.org/stable/c/5a28a4b22dde92f9d293b94236314b8d6181dc4a
- https://git.kernel.org/stable/c/63996ffc594d128ccec8fc0983f91effd2d3adc4
- https://git.kernel.org/stable/c/bc5bde9ce3cc36502839dfe98e068f7303a50982
- https://git.kernel.org/stable/c/dfe388da13aa784851e5ebbea90afbb099075761
- https://git.kernel.org/stable/c/e00f7d2b5f2540a3415a229c982af7a25ff6362e
- https://git.kernel.org/stable/c/e1e602d6b22d5cb1641c4459c487eb18bf569e0a
- https://git.kernel.org/stable/c/ed503eaad62f20cdd5122d7c3078a648a99c8f16
- https://git.kernel.org/stable/c/fd39e711866498ae94fcf9acf6f422a4f045b681
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74656.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74656
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
