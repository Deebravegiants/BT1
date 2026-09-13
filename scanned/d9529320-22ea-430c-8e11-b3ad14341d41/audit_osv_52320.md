# [M] CVE-2021-47325

## Summary
Severity: Medium
Advisory: CVE-2021-47325
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47325
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/arm-smmu: Fix arm_smmu_device refcount leak in address translation

The reference counting issue happens in several exception handling paths
of arm_smmu_iova_to_phys_hard(). When those error scenarios occur, the
function forgets to decrease the refcount of "smmu" increased by
arm_smmu_rpm_get(), causing a refcount leak.

Fix this issue by jumping to "out" label when those error scenarios
occur.

## References
- https://git.kernel.org/stable/c/5f9741a9a91f25c89e04b408cd61e3ab050ce24b
- https://git.kernel.org/stable/c/7c8f176d6a3fa18aa0f8875da6f7c672ed2a8554
- https://git.kernel.org/stable/c/b11220803ad14a2a880cc06d8e01fe2548cc85b0
- https://git.kernel.org/stable/c/0f0c5ea09139777d90729d408b807021f2ea6492
- https://git.kernel.org/stable/c/43d1aaa1965f9b58035196dac49b1e1e6c9c25eb
