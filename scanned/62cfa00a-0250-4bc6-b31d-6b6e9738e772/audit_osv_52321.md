# [H] CVE-2021-47327

## Summary
Severity: High
Advisory: CVE-2021-47327
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47327
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/arm-smmu: Fix arm_smmu_device refcount leak when arm_smmu_rpm_get fails

arm_smmu_rpm_get() invokes pm_runtime_get_sync(), which increases the
refcount of the "smmu" even though the return value is less than 0.

The reference counting issue happens in some error handling paths of
arm_smmu_rpm_get() in its caller functions. When arm_smmu_rpm_get()
fails, the caller functions forget to decrease the refcount of "smmu"
increased by arm_smmu_rpm_get(), causing a refcount leak.

Fix this issue by calling pm_runtime_resume_and_get() instead of
pm_runtime_get_sync() in arm_smmu_rpm_get(), which can keep the refcount
balanced in case of failure.

## References
- https://git.kernel.org/stable/c/1adf30f198c26539a62d761e45af72cde570413d
- https://git.kernel.org/stable/c/3761ae0d0e549f2acdaf11f49df4ed06d256b20f
- https://git.kernel.org/stable/c/c4007596fbdabc29f858dc2e1990858a146b60b2
- https://git.kernel.org/stable/c/fbf4daa6f4105e01fbd3868006f65c163365c1e3
- https://git.kernel.org/stable/c/fe92c058199067ae90cf2a901ddf3c271893557a
