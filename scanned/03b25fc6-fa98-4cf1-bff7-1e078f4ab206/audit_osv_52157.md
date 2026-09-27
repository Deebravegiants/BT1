# [M] CVE-2021-47140

## Summary
Severity: Medium
Advisory: CVE-2021-47140
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47140
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/amd: Clear DMA ops when switching domain

Since commit 08a27c1c3ecf ("iommu: Add support to change default domain
of an iommu group") a user can switch a device between IOMMU and direct
DMA through sysfs. This doesn't work for AMD IOMMU at the moment because
dev->dma_ops is not cleared when switching from a DMA to an identity
IOMMU domain. The DMA layer thus attempts to use the dma-iommu ops on an
identity domain, causing an oops:

  # echo 0000:00:05.0 > /sys/sys/bus/pci/drivers/e1000e/unbind
  # echo identity > /sys/bus/pci/devices/0000:00:05.0/iommu_group/type
  # echo 0000:00:05.0 > /sys/sys/bus/pci/drivers/e1000e/bind
   ...
  BUG: kernel NULL pointer dereference, address: 0000000000000028
   ...
   Call Trace:
    iommu_dma_alloc
    e1000e_setup_tx_resources
    e1000e_open

Since iommu_change_dev_def_domain() calls probe_finalize() again, clear
the dma_ops there like Vt-d does.

## References
- https://git.kernel.org/stable/c/d6177a6556f853785867e2ec6d5b7f4906f0d809
- https://git.kernel.org/stable/c/f3f2cf46291a693eab21adb94171b0128c2a9ec1
