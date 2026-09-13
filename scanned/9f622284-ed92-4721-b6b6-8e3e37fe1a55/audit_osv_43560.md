# [H] gpu: host1x: Fix iommu_map_sgtable() return value check

## Summary
Severity: High
Advisory: CVE-2026-74380
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74380
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpu: host1x: Fix iommu_map_sgtable() return value check

Commit "iommu: return full error code from iommu_map_sg[_atomic]()"
changed iommu_map_sgtable() to return an ssize_t and negative values
in error cases, rather than a size_t and a zero.

pin_job() also was incorrectly assigning to 'int', which could cause
overflows into negative values.

Update pin_job() to correctly check for errors from iommu_map_sgtable.

## References
- https://git.kernel.org/stable/c/18f74762013a4b6aa6f905c4459e0f506f9c5c7b
- https://git.kernel.org/stable/c/2a68928c445138961e2c451983b473aeb3f5b999
- https://git.kernel.org/stable/c/3ac173e46ef6fda9c9df8d47cdff4df962df9728
- https://git.kernel.org/stable/c/5f3985c2a500df3126cb12a2e0ccf26a40bc495d
- https://git.kernel.org/stable/c/79240eee5a40014d9edfabe19f06b35ffa84e5f8
- https://git.kernel.org/stable/c/e024c7993d839503d6c1f0044b8fc537c30300e9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74380.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74380
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
