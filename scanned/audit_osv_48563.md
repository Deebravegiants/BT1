# [M] CVE-2017-9605

## Summary
Severity: Medium
Advisory: CVE-2017-9605
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-06-13
Source: https://osv.dev/vulnerability/CVE-2017-9605
Type: osv

## Details
The vmw_gb_surface_define_ioctl function (accessible via DRM_IOCTL_VMW_GB_SURFACE_CREATE) in drivers/gpu/drm/vmwgfx/vmwgfx_surface.c in the Linux kernel through 4.11.4 defines a backup_handle variable but does not give it an initial value. If one attempts to create a GB surface, with a previously allocated DMA buffer to be used as a backup buffer, the backup_handle variable does not get written to and is then later returned to user space, allowing local users to obtain sensitive information from uninitialized kernel memory via a crafted ioctl call.

## References
- http://www.debian.org/security/2017/dsa-3945
- http://www.securityfocus.com/bid/99095
- http://www.debian.org/security/2017/dsa-3927
- https://github.com/torvalds/linux/commit/07678eca2cf9c9a18584e546c2b2a0d0c9a3150c
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=07678eca2cf9c9a18584e546c2b2a0d0c9a3150c
