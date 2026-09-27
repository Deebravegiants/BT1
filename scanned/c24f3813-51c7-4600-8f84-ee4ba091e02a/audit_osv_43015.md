# [H] accel/amdxdna: Fix potential amdxdna_umap lifetime race

## Summary
Severity: High
Advisory: CVE-2026-72328
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72328
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/amdxdna: Fix potential amdxdna_umap lifetime race

amdxdna_umap_release() calls the blocking mmu_interval_notifier_remove()
before removing the object from abo->mem.umap_list. If
aie2_populate_range() runs concurrently, it may obtain a reference to an
amdxdna_umap that is being released, leading to a potential use-after-free.

Use kref_get_unless_zero() in aie2_populate_range() when acquiring a
reference. If the reference count has already dropped to zero, release
is in progress and the entry is skipped.

## References
- https://git.kernel.org/stable/c/14f172eff9c19f8043a9858845f33cd034f3a41e
- https://git.kernel.org/stable/c/267809e2c56fbea486f7250c8a4acddcc3c54dc5
- https://git.kernel.org/stable/c/91e8109ecffb925b6202d2737384df285b195bfb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72328.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72328
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
