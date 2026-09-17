# [H] ipv6: anycast: insert aca into global hash under idev->lock

## Summary
Severity: High
Advisory: CVE-2026-53259
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53259
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: anycast: insert aca into global hash under idev->lock

syzbot reported a splat [1]: a slab-use-after-free in
ipv6_chk_acast_addr(), which walks the global inet6_acaddr_lst[] hash
under RCU and dereferences a struct ifacaddr6 that has already been
freed while still linked in the hash, so a later reader walks into a
dangling node.

In __ipv6_dev_ac_inc() the aca is allocated with refcount 1, then
aca_get() bumps it to 2 to keep it alive across the unlocked region.
It is published to idev->ac_list under idev->lock, but
ipv6_add_acaddr_hash() runs after write_unlock_bh(). A concurrent
teardown (ipv6_ac_destroy_dev() from addrconf_ifdown(), under RTNL)
can slip into that window:

  CPU0 __ipv6_dev_ac_inc           CPU1 ipv6_ac_destroy_dev (RTNL)
  ------------------------------   ------------------------------------
  aca_alloc()              refcnt 1
  aca_get()               refcnt 2
  write_lock_bh(idev->lock)
    add aca to ac_list
  write_unlock_bh(idev->lock)
                                   write_lock_bh(idev->lock)
                                     pull aca off ac_list
                                   write_unlock_bh(idev->lock)
                                   ipv6_del_acaddr_hash(aca)
                                     hlist_del_init_rcu() is a no-op,
                                     aca is not in the hash yet
                                   aca_put()           refcnt 2->1
  ipv6_add_acaddr_hash(aca)
    aca now inserted into the hash
  aca_put()                refcnt 1->0
    call_rcu(aca_free_rcu) -> kfree(aca)

The hash removal becomes a no-op because the insertion has not
happened yet, so once CPU0 inserts and drops the last reference, the
aca is freed while still linked in inet6_acaddr_lst[], and readers
dereference freed memory after the slab slot is reused.

This window opened once RTNL stopped serializing the join path against
device teardown. Move ipv6_add_acaddr_hash() inside the idev->lock
section so the ac_list and hash insertions are atomic with respect to
teardown: a racing remover now either misses the aca entirely or finds
it in both lists.

acaddr_hash_lock is now nested under idev->lock, which is acquired in
softirq context, so switch all acaddr_hash_lock sites to spin_lock_bh()
to avoid the irq lock inversion reported in [2].

[1] https://syzkaller.appspot.com/bug?extid=a01df04303c131efbf3a
[2] https://lore.kernel.org/netdev/6a194ef7.ba3b1513.1890b4.0000.GAE@google.com/

## References
- https://git.kernel.org/stable/c/15be7e9fdbff831fb3e89b83cc337a4f85ad3310
- https://git.kernel.org/stable/c/3a967c498baa976b11d4800dda224c507416e97c
- https://git.kernel.org/stable/c/f723ccaff2fb72b71ae8a9fd283f0dee4d9ae7a3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53259.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53259
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
