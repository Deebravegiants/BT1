# [M] mm: memcg: fix NULL pointer in mem_cgroup_track_foreign_dirty_slowpath()

## Summary
Severity: Medium
Advisory: CVE-2023-52939
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-52939
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <6.1.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: memcg: fix NULL pointer in mem_cgroup_track_foreign_dirty_slowpath()

As commit 18365225f044 ("hwpoison, memcg: forcibly uncharge LRU pages"),
hwpoison will forcibly uncharg a LRU hwpoisoned page, the folio_memcg
could be NULl, then, mem_cgroup_track_foreign_dirty_slowpath() could
occurs a NULL pointer dereference, let's do not record the foreign
writebacks for folio memcg is null in mem_cgroup_track_foreign_dirty() to
fix it.

## References
- https://git.kernel.org/stable/c/ac86f547ca1002aec2ef66b9e64d03f45bbbfbb9
- https://git.kernel.org/stable/c/b79ba5953f6fdc5559389ad415620bffc24f024b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52939.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52939
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
