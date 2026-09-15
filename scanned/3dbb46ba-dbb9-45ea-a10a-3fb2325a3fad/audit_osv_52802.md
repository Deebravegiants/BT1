# [H] CVE-2022-1419

## Summary
Severity: High
Advisory: CVE-2022-1419
Aliases: A-235540888, PUB-A-235540888
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-02
Source: https://osv.dev/vulnerability/CVE-2022-1419
Type: osv

## Details
The root cause of this vulnerability is that the ioctl$DRM_IOCTL_MODE_DESTROY_DUMB can decrease refcount of *drm_vgem_gem_object *(created in *vgem_gem_dumb_create*) concurrently, and *vgem_gem_dumb_create *will access the freed drm_vgem_gem_object.

## References
- https://www.debian.org/security/2022/dsa-5173
- https://bugzilla.redhat.com/show_bug.cgi?id=2077560
