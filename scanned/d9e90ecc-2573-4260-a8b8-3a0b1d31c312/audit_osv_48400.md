# [M] CVE-2017-7346

## Summary
Severity: Medium
Advisory: CVE-2017-7346
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-30
Source: https://osv.dev/vulnerability/CVE-2017-7346
Type: osv

## Details
The vmw_gb_surface_define_ioctl function in drivers/gpu/drm/vmwgfx/vmwgfx_surface.c in the Linux kernel through 4.10.7 does not validate certain levels data, which allows local users to cause a denial of service (system hang) via a crafted ioctl call for a /dev/dri/renderD* device.

## References
- http://www.debian.org/security/2017/dsa-3927
- http://www.debian.org/security/2017/dsa-3945
- http://www.securityfocus.com/bid/97257
- https://lists.freedesktop.org/archives/dri-devel/2017-March/137429.html
- http://marc.info/?l=linux-kernel&m=149086968410117&w=2
- https://bugzilla.redhat.com/show_bug.cgi?id=1437431
