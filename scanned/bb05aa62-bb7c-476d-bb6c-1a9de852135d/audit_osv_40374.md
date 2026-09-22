# [H] iommu/riscv: Add IOTINVAL after updating DDT/PDT entries

## Summary
Severity: High
Advisory: CVE-2026-53057
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53057
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/riscv: Add IOTINVAL after updating DDT/PDT entries

Add riscv_iommu_iodir_iotinval() to perform required TLB and context cache
invalidations after updating DDT or PDT entries, as mandated by the RISC-V
IOMMU specification (Section 6.3.1 and 6.3.2).

## References
- https://git.kernel.org/stable/c/3f917d9bff68600f77561900f3145bd4706dc840
- https://git.kernel.org/stable/c/d99d1c13faa793ff1abab0d20ab6473c838081b3
- https://git.kernel.org/stable/c/f5c262b544975e067ea265fc7403aefbbea8563e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53057.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53057
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
