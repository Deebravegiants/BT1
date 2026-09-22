# [M] iommu/arm-smmu: fix possible null-ptr-deref in arm_smmu_device_probe()

## Summary
Severity: Medium
Advisory: CVE-2022-49323
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49323
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/arm-smmu: fix possible null-ptr-deref in arm_smmu_device_probe()

It will cause null-ptr-deref when using 'res', if platform_get_resource()
returns NULL, so move using 'res' after devm_ioremap_resource() that
will check it to avoid null-ptr-deref.
And use devm_platform_get_and_ioremap_resource() to simplify code.

## References
- https://git.kernel.org/stable/c/3660db29b0305f9a1d95979c7af0f5db6ea99f5d
- https://git.kernel.org/stable/c/449fc4561762ad9ad85362d5f01f0d0df397457a
- https://git.kernel.org/stable/c/80776a71340f57d6a4952635fc89f0342072f3ca
- https://git.kernel.org/stable/c/98dd53a92825747395649f54d23512a13c3ed471
- https://git.kernel.org/stable/c/d9ed8af1dee37f181096631fb03729ece98ba816
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49323.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49323
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
