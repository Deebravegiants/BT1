# [H] wifi: mac80211: fix unsol_bcast_probe_resp double free on alloc failure

## Summary
Severity: High
Advisory: CVE-2026-64568
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-64568
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: fix unsol_bcast_probe_resp double free on alloc failure

ieee80211_set_unsol_bcast_probe_resp() calls kfree_rcu() on the old
template before allocating the replacement. If the kzalloc() then fails,
it returns -ENOMEM while link->u.ap.unsol_bcast_probe_resp still points
at the object already queued for freeing. A later update or AP teardown
re-queues that same rcu_head; the second free is caught by KASAN when the
RCU sheaf is processed in softirq:

  BUG: KASAN: double-free in rcu_free_sheaf (mm/slub.c:5850)
  Free of addr ffff88800d06f300 by task exploit/145
   ...
   __rcu_free_sheaf_prepare (mm/slub.c:2634 mm/slub.c:2940)
   rcu_free_sheaf (mm/slub.c:5850)
   rcu_core (kernel/rcu/tree.c:2617 kernel/rcu/tree.c:2869)
   handle_softirqs (kernel/softirq.c:622)
  The buggy address belongs to the cache kmalloc-128 of size 128

Queue the old object for kfree_rcu() only after the new one is published,
matching ieee80211_set_probe_resp() and ieee80211_set_s1g_short_beacon().

## References
- https://git.kernel.org/stable/c/0ace76e410d7f7d813b605825a3e593a79c3958f
- https://git.kernel.org/stable/c/1d067abcd37062426c59ec73dbc4e87a63f33fea
- https://git.kernel.org/stable/c/ca27a81cd77b698e5eb586a011bee6800c7ee4bd
- https://git.kernel.org/stable/c/d62b55b7c7dc62887d7fd5648fb38f0bfaef53ae
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64568.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64568
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
