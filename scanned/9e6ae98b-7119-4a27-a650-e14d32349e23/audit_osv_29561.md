# [H] mm: list_lru: fix UAF for memory cgroup

## Summary
Severity: High
Advisory: CVE-2024-43888
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-26
Source: https://osv.dev/vulnerability/CVE-2024-43888
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.10.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: list_lru: fix UAF for memory cgroup

The mem_cgroup_from_slab_obj() is supposed to be called under rcu lock or
cgroup_mutex or others which could prevent returned memcg from being
freed.  Fix it by adding missing rcu read lock.

Found by code inspection.

[songmuchun@bytedance.com: only grab rcu lock when necessary, per Vlastimil]

## References
- https://git.kernel.org/stable/c/4589f77c18dd98b65f45617b6d1e95313cf6fcab
- https://git.kernel.org/stable/c/5161b48712dcd08ec427c450399d4d1483e21dea
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43888.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43888
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
