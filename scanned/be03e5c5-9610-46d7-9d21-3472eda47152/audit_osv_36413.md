# [H] iommu/sva: Fix crash in iommu_sva_unbind_device()

## Summary
Severity: High
Advisory: CVE-2026-23429
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-23429
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/sva: Fix crash in iommu_sva_unbind_device()

domain->mm->iommu_mm can be freed by iommu_domain_free():
  iommu_domain_free()
    mmdrop()
      __mmdrop()
        mm_pasid_drop()
After iommu_domain_free() returns, accessing domain->mm->iommu_mm may
dereference a freed mm structure, leading to a crash.

Fix this by moving the code that accesses domain->mm->iommu_mm to before
the call to iommu_domain_free().

## References
- https://git.kernel.org/stable/c/06e14c36e20b48171df13d51b89fe67c594ed07a
- https://git.kernel.org/stable/c/58abeb7b9562f25bdfa2f5ae5ce803eb02e74433
- https://git.kernel.org/stable/c/f5daaa2c959d9f894fb5b1ab76da8612dd220a0d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23429.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23429
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
