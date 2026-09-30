# [M] CVE-2017-7261

## Summary
Severity: Medium
Advisory: CVE-2017-7261
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-24
Source: https://osv.dev/vulnerability/CVE-2017-7261
Type: osv

## Details
The vmw_surface_define_ioctl function in drivers/gpu/drm/vmwgfx/vmwgfx_surface.c in the Linux kernel through 4.10.5 does not check for a zero value of certain levels data, which allows local users to cause a denial of service (ZERO_SIZE_PTR dereference, and GPF and possibly panic) via a crafted ioctl call for a /dev/dri/renderD* device.

## References
- http://www.securityfocus.com/bid/97096
- http://marc.info/?t=149037004200005&r=1&w=2
- https://lists.freedesktop.org/archives/dri-devel/2017-March/136814.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1435719
