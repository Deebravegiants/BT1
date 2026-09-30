# [H] vfio/pci: Clean up DMABUFs before disabling function

## Summary
Severity: High
Advisory: CVE-2026-53322
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-53322
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

vfio/pci: Clean up DMABUFs before disabling function

On device shutdown, make vfio_pci_core_close_device() call
vfio_pci_dma_buf_cleanup() before the function is disabled via
vfio_pci_core_disable().  This ensures that all access via DMABUFs is
revoked before the function's BARs become inaccessible.

This fixes an issue where, if the function is disabled first, a tiny
window exists in which the function's MSE is cleared and yet BARs
could still be accessed via the DMABUF.  The resources would also be
freed and up for grabs by a different driver.

## References
- https://git.kernel.org/stable/c/4f1000a30f67cf7d328059242776a858611d5ef9
- https://git.kernel.org/stable/c/d97708701434ce72968e771976aaf9d3438fcafd
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53322.json
- https://access.redhat.com/errata/RHSA-2026:65334
- https://access.redhat.com/security/cve/CVE-2026-53322
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53322.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53322
- https://bugzilla.redhat.com/show_bug.cgi?id=2493709
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
