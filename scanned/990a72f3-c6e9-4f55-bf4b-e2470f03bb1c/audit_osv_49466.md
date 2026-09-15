# [H] CVE-2019-12881

## Summary
Severity: High
Advisory: CVE-2019-12881
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-18
Source: https://osv.dev/vulnerability/CVE-2019-12881
Type: osv

## Details
i915_gem_userptr_get_pages in drivers/gpu/drm/i915/i915_gem_userptr.c in the Linux kernel 4.15.0 on Ubuntu 18.04.2 allows local users to cause a denial of service (NULL pointer dereference and BUG) or possibly have unspecified other impact via crafted ioctl calls to /dev/dri/card0.

## References
- http://www.securityfocus.com/bid/108873
- https://security.netapp.com/advisory/ntap-20190710-0002/
- https://gist.github.com/oxagast/472866fb2c3d439e10499d7141d0a520
