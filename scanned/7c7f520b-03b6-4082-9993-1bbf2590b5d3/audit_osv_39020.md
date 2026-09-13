# [H] net: nexthop: fix percpu use-after-free in remove_nh_grp_entry

## Summary
Severity: High
Advisory: CVE-2026-43374
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43374
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: nexthop: fix percpu use-after-free in remove_nh_grp_entry

When removing a nexthop from a group, remove_nh_grp_entry() publishes
the new group via rcu_assign_pointer() then immediately frees the
removed entry's percpu stats with free_percpu(). However, the
synchronize_net() grace period in the caller remove_nexthop_from_groups()
runs after the free. RCU readers that entered before the publish still
see the old group and can dereference the freed stats via
nh_grp_entry_stats_inc() -> get_cpu_ptr(nhge->stats), causing a
use-after-free on percpu memory.

Fix by deferring the free_percpu() until after synchronize_net() in the
caller. Removed entries are chained via nh_list onto a local deferred
free list. After the grace period completes and all RCU readers have
finished, the percpu stats are safely freed.

## References
- https://git.kernel.org/stable/c/9e08ad731862b22a87cc55f752e16d66cdc9e231
- https://git.kernel.org/stable/c/ab5ebab9664214ba41a7633cb4e72f128204f924
- https://git.kernel.org/stable/c/abf4feaee6405f1441929c6ebe7a250f2cd170a7
- https://git.kernel.org/stable/c/b2662e7593e94ae09b1cf7ee5f09160a3612bcb2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43374.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43374
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
