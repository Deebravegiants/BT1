# [H] fbdev/ep93xx-fb: Do not assign to struct fb_info.dev

## Summary
Severity: High
Advisory: CVE-2023-53314
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53314
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.32 <4.14.326, >=4.15.0 <4.19.295, >=4.20.0 <5.4.257, >=5.5.0 <5.10.195, >=5.11.0 <5.15.132, >=5.16.0 <6.1.54, >=6.2.0 <6.5.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

fbdev/ep93xx-fb: Do not assign to struct fb_info.dev

Do not assing the Linux device to struct fb_info.dev. The call to
register_framebuffer() initializes the field to the fbdev device.
Drivers should not override its value.

Fixes a bug where the driver incorrectly decreases the hardware
device's reference counter and leaks the fbdev device.

v2:
	* add Fixes tag (Dan)

## References
- https://git.kernel.org/stable/c/0517fc5a71333b315164736bbd32608894fbb872
- https://git.kernel.org/stable/c/1c6ff2a7c593db851f23e31ace2baf557ea9d0ff
- https://git.kernel.org/stable/c/309c27162afea79b3c7f8747bb650faf6923b639
- https://git.kernel.org/stable/c/4aade6c9100a3537788b6a9c7ac481037d19efdf
- https://git.kernel.org/stable/c/8ffa40ff64aa43a9a28fcf209b48d86a3e0f4972
- https://git.kernel.org/stable/c/f83c1b13f8154e0284448912756d0a351a1a602a
- https://git.kernel.org/stable/c/f90a0e5265b60cdd3c77990e8105f79aa2fac994
- https://git.kernel.org/stable/c/ffdf2b020db717853167391a3a8d912e13428fa6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53314.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53314
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
