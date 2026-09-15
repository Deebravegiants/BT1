# [H] bpf: Use RCU-safe iteration in dev_map_redirect_multi() SKB path

## Summary
Severity: High
Advisory: CVE-2026-53096
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53096
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Use RCU-safe iteration in dev_map_redirect_multi() SKB path

The DEVMAP_HASH branch in dev_map_redirect_multi() uses
hlist_for_each_entry_safe() to iterate hash buckets, but this function
runs under RCU protection (called from xdp_do_generic_redirect_map()
in softirq context). Concurrent writers (__dev_map_hash_update_elem,
dev_map_hash_delete_elem) modify the list using RCU primitives
(hlist_add_head_rcu, hlist_del_rcu).

hlist_for_each_entry_safe() performs plain pointer dereferences without
rcu_dereference(), missing the acquire barrier needed to pair with
writers' rcu_assign_pointer(). On weakly-ordered architectures (ARM64,
POWER), a reader can observe a partially-constructed node. It also
defeats CONFIG_PROVE_RCU lockdep validation and KCSAN data-race
detection.

Replace with hlist_for_each_entry_rcu() using rcu_read_lock_bh_held()
as the lockdep condition, consistent with the rcu_dereference_check()
used in the DEVMAP (non-hash) branch of the same functions. Also fix
the same incorrect lockdep_is_held(&dtab->index_lock) condition in
dev_map_enqueue_multi(), where the lock is not held either.

## References
- https://git.kernel.org/stable/c/4a3d0fe30b907ff324b1b49756f7e713d67f3645
- https://git.kernel.org/stable/c/571a05ea1baaccc0dc1e0d227b2cbc978b96d392
- https://git.kernel.org/stable/c/7027e705062482a8cea43a1c13ede3c35653966f
- https://git.kernel.org/stable/c/8ed82f807bb09d2c8455aaa665f2c6cb17bc6a19
- https://git.kernel.org/stable/c/b089aa6e94d7a08e74d076a0fe274842dc9feccc
- https://git.kernel.org/stable/c/cb2c1f3cf65b855548e1b8d55a08bfbaa5a0901a
- https://git.kernel.org/stable/c/d4c4bd231ebad70e6f30db429e9640bf378b2f52
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53096.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53096
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
