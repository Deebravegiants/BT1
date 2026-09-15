# [C] iommu/arm-smmu-v3-iommufd: Require exactly one Stream ID for a vDEVICE

## Summary
Severity: Critical
Advisory: CVE-2026-74573
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74573
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/arm-smmu-v3-iommufd: Require exactly one Stream ID for a vDEVICE

arm_vsmmu_vsid_to_sid() maps a guest's vSID to a single physical Stream ID
taken from master->streams[0], assuming a device has exactly one stream. A
device with several streams gets only its first one mapped, so a guest vSID
invalidation cannot reach the others' ATC and IOTLB entries; a device with
none makes master->streams a ZERO_SIZE_PTR, read out of bounds.

Add an arm_vsmmu_vdevice_init() op to reject the vDEVICE with -EOPNOTSUPP
when master->num_streams is not one, rather than mapping it silently.

## References
- https://git.kernel.org/stable/c/0acbc621341aca4eb94d9c2f43e1ab273ff088f0
- https://git.kernel.org/stable/c/3808bab5d95ae79e333e11f6a73d178e084c645d
- https://git.kernel.org/stable/c/c3b8ee84a965058b41275069d4696f37a8b14bf6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74573.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74573
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
