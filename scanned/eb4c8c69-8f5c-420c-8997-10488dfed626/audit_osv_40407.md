# [H] mm/list_lru: drain before clearing xarray entry on reparent

## Summary
Severity: High
Advisory: CVE-2026-53153
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53153
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/list_lru: drain before clearing xarray entry on reparent

memcg_reparent_list_lrus() clears the dying memcg's xarray entry with
xas_store(&xas, NULL) before reparenting its per-node lists into the
parent.  This opens a window where a concurrent list_lru_del() arriving
for the dying memcg sees xa_load() == NULL, walks to the parent in
lock_list_lru_of_memcg(), takes the parent's per-node lock, and calls
list_del_init() on an item still physically linked on the dying memcg's
list.

If another in-flight thread holds the dying memcg's per-node lock at the
same moment (another list_lru_del, or a list_lru_walk_one running an
isolate callback), both threads modify ->next/->prev pointers on the same
physical list under different locks.  Adjacent items can corrupt each
other's links.

Fix it by reversing the order: reparent each per-node list and mark the
child's list lru dead and then clear the xarray entry.  Any concurrent
list_lru op that finds the still-set xarray entry either takes the dying
memcg's per-node lock (synchronizing with the drain) or sees LONG_MIN and
walks to the parent, where the items now live.

## References
- https://git.kernel.org/stable/c/2b66496d794e98f7aeec7688573051f22ec40bac
- https://git.kernel.org/stable/c/98733f3f0becb1ae0701d021c1748e974e5fa55c
- https://git.kernel.org/stable/c/c19ff4351214f059349788e13e70e74325831ff6
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53153.json
- https://access.redhat.com/errata/RHSA-2026:61887
- https://access.redhat.com/security/cve/CVE-2026-53153
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53153.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53153
- https://bugzilla.redhat.com/show_bug.cgi?id=2492790
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
