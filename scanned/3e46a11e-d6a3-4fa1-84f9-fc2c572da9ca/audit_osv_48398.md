# [H] CVE-2017-7294

## Summary
Severity: High
Advisory: CVE-2017-7294
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-29
Source: https://osv.dev/vulnerability/CVE-2017-7294
Type: osv

## Details
The vmw_surface_define_ioctl function in drivers/gpu/drm/vmwgfx/vmwgfx_surface.c in the Linux kernel through 4.10.6 does not validate addition of certain levels data, which allows local users to trigger an integer overflow and out-of-bounds write, and cause a denial of service (system hang or crash) or possibly gain privileges, via a crafted ioctl call for a /dev/dri/renderD* device.

## References
- http://www.securityfocus.com/bid/97177
- https://access.redhat.com/errata/RHSA-2018:0676
- https://access.redhat.com/errata/RHSA-2018:1062
- https://bugzilla.redhat.com/show_bug.cgi?id=1436798
- https://lists.freedesktop.org/archives/dri-devel/2017-March/137094.html
