# [H] iommu: Handle unmap error when iommu_debug is enabled

## Summary
Severity: High
Advisory: CVE-2026-64152
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64152
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu: Handle unmap error when iommu_debug is enabled

Sashiko noticed a latent bug where the map error flow called iommu_unmap()
which calls iommu_debug_unmap_begin()/iommu_debug_unmap_end() however
since this is an error path the map flow never actually established the
original iommu_debug_map() it will malfunction.

Lift the unmap error handling into iommu_map_nosync() and reorder it so
the trace_map()/iommu_debug_map() records the partial mapping and then
immediately unmaps it. This avoid creating the unbalanced tracking and
provides saner tracing instead of a unmap unmatched to any map.

## References
- https://git.kernel.org/stable/c/0735c54804c709d1b292f3b6947cfb560b2ce552
- https://git.kernel.org/stable/c/0cd028806efc148a75d4acf711d21db335a89661
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64152.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64152
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
