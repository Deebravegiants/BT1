# [H] iommupt: Check for missing PAGE_SIZE in the pgsize_bitmap

## Summary
Severity: High
Advisory: CVE-2026-64151
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64151
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommupt: Check for missing PAGE_SIZE in the pgsize_bitmap

Sashiko pointed out that the driver could drop PAGE_SIZE from the
pgsize_bitmap. That is technically allowed but nothing does it, and
such an iommu_domain would not be used with the DMA API today.

Still, it is against the design and it is trivial to fix up. Lift
the PT_WARN_ON to the if branch and just skip the fast path.

## References
- https://git.kernel.org/stable/c/00850f41da24423587abd6124a790dd4f12bcef3
- https://git.kernel.org/stable/c/8ef3f77c440005c7f04229a75976bfc078364247
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64151.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64151
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
