# [H] iommu/vt-d: Use device rbtree in iopf reporting path

## Summary
Severity: High
Advisory: CVE-2024-35843
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35843
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/vt-d: Use device rbtree in iopf reporting path

The existing I/O page fault handler currently locates the PCI device by
calling pci_get_domain_bus_and_slot(). This function searches the list
of all PCI devices until the desired device is found. To improve lookup
efficiency, replace it with device_rbtree_find() to search the device
within the probed device rbtree.

The I/O page fault is initiated by the device, which does not have any
synchronization mechanism with the software to ensure that the device
stays in the probed device tree. Theoretically, a device could be released
by the IOMMU subsystem after device_rbtree_find() and before
iopf_get_dev_fault_param(), which would cause a use-after-free problem.

Add a mutex to synchronize the I/O page fault reporting path and the IOMMU
release device path. This lock doesn't introduce any performance overhead,
as the conflict between I/O page fault reporting and device releasing is
very rare.

## References
- https://git.kernel.org/stable/c/3d39238991e745c5df85785604f037f35d9d1b15
- https://git.kernel.org/stable/c/def054b01a867822254e1dda13d587f5c7a99e2a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35843.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35843
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
