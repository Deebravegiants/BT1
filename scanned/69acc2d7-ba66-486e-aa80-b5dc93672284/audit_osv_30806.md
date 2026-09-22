# [M] iommu/arm-smmu: Defer probe of clients after smmu device bound

## Summary
Severity: Medium
Advisory: CVE-2024-56568
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56568
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/arm-smmu: Defer probe of clients after smmu device bound

Null pointer dereference occurs due to a race between smmu
driver probe and client driver probe, when of_dma_configure()
for client is called after the iommu_device_register() for smmu driver
probe has executed but before the driver_bound() for smmu driver
has been called.

Following is how the race occurs:

T1:Smmu device probe		T2: Client device probe

really_probe()
arm_smmu_device_probe()
iommu_device_register()
					really_probe()
					platform_dma_configure()
					of_dma_configure()
					of_dma_configure_id()
					of_iommu_configure()
					iommu_probe_device()
					iommu_init_device()
					arm_smmu_probe_device()
					arm_smmu_get_by_fwnode()
						driver_find_device_by_fwnode()
						driver_find_device()
						next_device()
						klist_next()
						    /* null ptr
						       assigned to smmu */
					/* null ptr dereference
					   while smmu->streamid_mask */
driver_bound()
	klist_add_tail()

When this null smmu pointer is dereferenced later in
arm_smmu_probe_device, the device crashes.

Fix this by deferring the probe of the client device
until the smmu device has bound to the arm smmu driver.

[will: Add comment]

## References
- https://git.kernel.org/stable/c/229e6ee43d2a160a1592b83aad620d6027084aad
- https://git.kernel.org/stable/c/4a9485918a042e3114890dfbe19839a1897f8b2c
- https://git.kernel.org/stable/c/5018696b19bc6c021e934a8a59f4b1dd8c0ac9f8
- https://git.kernel.org/stable/c/c2527d07c7e9cda2c6165d5edccf74752baac1b0
- https://git.kernel.org/stable/c/dc02407ea952e20c544a078a6be2e6f008327973
- https://git.kernel.org/stable/c/f8f794f387ad21c4696e5cd0626cb6f8a5f6aea5
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56568.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56568
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
