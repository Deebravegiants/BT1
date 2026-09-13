# [M] CVE-2021-47177

## Summary
Severity: Medium
Advisory: CVE-2021-47177
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47177
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/vt-d: Fix sysfs leak in alloc_iommu()

iommu_device_sysfs_add() is called before, so is has to be cleaned on subsequent
errors.

## References
- https://git.kernel.org/stable/c/044bbe8b92ab4e542de7f6c93c88ea65cccd8e29
- https://git.kernel.org/stable/c/0ee74d5a48635c848c20f152d0d488bf84641304
- https://git.kernel.org/stable/c/22da9f4978381a99f1abaeaf6c9b83be6ab5ddd8
- https://git.kernel.org/stable/c/2ec5e9bb6b0560c90d315559c28a99723c80b996
- https://git.kernel.org/stable/c/ca466561eef36d1ec657673e3944eb6340bddb5b
- https://git.kernel.org/stable/c/f01134321d04f47c718bb41b799bcdeda27873d2
