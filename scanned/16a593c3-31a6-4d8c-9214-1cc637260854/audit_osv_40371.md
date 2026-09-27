# [H] iommu/amd: Fix clone_alias() to use the original device's devid

## Summary
Severity: High
Advisory: CVE-2026-53053
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53053
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/amd: Fix clone_alias() to use the original device's devid

Currently clone_alias() assumes first argument (pdev) is always the
original device pointer. This function is called by
pci_for_each_dma_alias() which based on topology decides to send
original or alias device details in first argument.

This meant that the source devid used to look up and copy the DTE
may be incorrect, leading to wrong or stale DTE entries being
propagated to alias device.

Fix this by passing the original pdev as the opaque data argument to
both the direct clone_alias() call and pci_for_each_dma_alias(). Inside
clone_alias(), retrieve the original device from data and compute devid
from it.

## References
- https://git.kernel.org/stable/c/20b3c566e2702e5d4d0545be8a97029a2eebcc0e
- https://git.kernel.org/stable/c/dae251ff11d2d2208a029f98923756831cefec46
- https://git.kernel.org/stable/c/dbd76a537d8cb814e7f5b795ab21ecb7949c821d
- https://git.kernel.org/stable/c/faad224fe0f0857a04ff2eb3c90f0de57f47d0f3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53053.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53053
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
