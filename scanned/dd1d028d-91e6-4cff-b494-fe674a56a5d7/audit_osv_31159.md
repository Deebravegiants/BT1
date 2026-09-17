# [H] drm/fbdev-dma: Add shadow buffering for deferred I/O

## Summary
Severity: High
Advisory: CVE-2024-58091
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2024-58091
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.36, >=6.13.0 <6.13.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/fbdev-dma: Add shadow buffering for deferred I/O

DMA areas are not necessarily backed by struct page, so we cannot
rely on it for deferred I/O. Allocate a shadow buffer for drivers
that require deferred I/O and use it as framebuffer memory.

Fixes driver errors about being "Unable to handle kernel NULL pointer
dereference at virtual address" or "Unable to handle kernel paging
request at virtual address".

The patch splits drm_fbdev_dma_driver_fbdev_probe() in an initial
allocation, which creates the DMA-backed buffer object, and a tail
that sets up the fbdev data structures. There is a tail function for
direct memory mappings and a tail function for deferred I/O with
the shadow buffer.

It is no longer possible to use deferred I/O without shadow buffer.
It can be re-added if there exists a reliably test for usable struct
page in the allocated DMA-backed buffer object.

## References
- https://git.kernel.org/stable/c/0d087de947babf7ed70029d042abcc6ed06ff415
- https://git.kernel.org/stable/c/3603996432997f7c88da37a97062a46cda01ac9d
- https://git.kernel.org/stable/c/cdc581169942de3b9e2648cfbd98c5ff9111c2c8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58091.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58091
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
