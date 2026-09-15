# [H] vfio/pci: Fix double free in dma-buf feature

## Summary
Severity: High
Advisory: CVE-2026-31468
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31468
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

vfio/pci: Fix double free in dma-buf feature

The error path through vfio_pci_core_feature_dma_buf() ignores its
own advice to only use dma_buf_put() after dma_buf_export(), instead
falling through the entire unwind chain.  In the unlikely event that
we encounter file descriptor exhaustion, this can result in an
unbalanced refcount on the vfio device and double free of allocated
objects.

Avoid this by moving the "put" directly into the error path and return
the errno rather than entering the unwind chain.

## References
- https://git.kernel.org/stable/c/83ad334afc9a645cef1062f5346526b1e36d6516
- https://git.kernel.org/stable/c/e98137f0a874ab36d0946de4707aa48cb7137d1c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31468.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31468
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
