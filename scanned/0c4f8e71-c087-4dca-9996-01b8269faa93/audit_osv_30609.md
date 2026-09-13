# [M] iommu/tegra241-cmdqv: Fix alignment failure at max_n_shift

## Summary
Severity: Medium
Advisory: CVE-2024-53225
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53225
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/tegra241-cmdqv: Fix alignment failure at max_n_shift

When configuring a kernel with PAGE_SIZE=4KB, depending on its setting of
CONFIG_CMA_ALIGNMENT, VCMDQ_LOG2SIZE_MAX=19 could fail the alignment test
and trigger a WARN_ON:
    WARNING: at drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3.c:3646
    Call trace:
     arm_smmu_init_one_queue+0x15c/0x210
     tegra241_cmdqv_init_structures+0x114/0x338
     arm_smmu_device_probe+0xb48/0x1d90

Fix it by capping max_n_shift to CMDQ_MAX_SZ_SHIFT as SMMUv3 CMDQ does.

## References
- https://git.kernel.org/stable/c/85a1d70b86dbcb84a68e7e4942a5181276945988
- https://git.kernel.org/stable/c/a3799717b881aa0f4e722afb70e7b8ba84ae4f36
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53225.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53225
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
