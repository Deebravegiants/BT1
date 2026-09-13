# [M] CVE-2019-19927

## Summary
Severity: Medium
Advisory: CVE-2019-19927
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-12-31
Source: https://osv.dev/vulnerability/CVE-2019-19927
Type: osv

## Details
In the Linux kernel 5.0.0-rc7 (as distributed in ubuntu/linux.git on kernel.ubuntu.com), mounting a crafted f2fs filesystem image and performing some operations can lead to slab-out-of-bounds read access in ttm_put_pages in drivers/gpu/drm/ttm/ttm_page_alloc.c. This is related to the vmwgfx or ttm module.

## References
- https://security.netapp.com/advisory/ntap-20200204-0002/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://github.com/torvalds/linux/commit/a66477b0efe511d98dde3e4aaeb189790e6f0a39
- https://github.com/torvalds/linux/commit/ac1e516d5a4c56bf0cb4a3dfc0672f689131cfd4
- https://github.com/torvalds/linux/commit/453393369dc9806d2455151e329c599684762428
- https://github.com/bobfuzzer/CVE/tree/master/CVE-2019-19927
