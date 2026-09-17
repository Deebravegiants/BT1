# [H] vfio/pci: Release the VGA arbiter client on register_device() failure

## Summary
Severity: High
Advisory: CVE-2026-64475
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64475
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.261, >=5.11.0 <5.15.212, >=5.13.0 <6.1.178, >=5.16.0 <6.6.145, >=6.2.0 <6.12.96, >=6.7.0 <6.18.39, >=6.13.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

vfio/pci: Release the VGA arbiter client on register_device() failure

The re-order in the Fixes commit below displaced vfio_pci_vga_init() as
the last failure point of what is now vfio_pci_core_register_device()
without introducing an unwind for the VGA arbiter registration.

In current kernels this is mostly benign because vfio_pci_set_decode()
only uses pci_dev state, but the original failure path could leave a
callback with a freed vdev cookie.  The stale registration also becomes
unsafe again once the callback follows drvdata to the vfio device.

Add the required VGA unwind callout.

## References
- https://git.kernel.org/stable/c/0f2a35a0c7ea7da347b814750eaa78adf3582381
- https://git.kernel.org/stable/c/278a5659c391fe5afe5f9ce1bad1fd24e90144f1
- https://git.kernel.org/stable/c/42d758a09d2c46c42357ecde9a5492f015bde2e5
- https://git.kernel.org/stable/c/52adb2dff7ce3d8430e2bdc5988b618a430def85
- https://git.kernel.org/stable/c/8d65decde9afd2bd78bcfffdc0df73b82a0b5509
- https://git.kernel.org/stable/c/9e0a3f642e607848669235f5069f35640abbfc88
- https://git.kernel.org/stable/c/daedde7f024ecf88bc8e832ed40cf2c795f0796a
- https://git.kernel.org/stable/c/ef4c38d30b3744e89eb5048218904bb629ea8d47
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64475.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64475
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
