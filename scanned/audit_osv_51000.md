# [H] CVE-2020-7053

## Summary
Severity: High
Advisory: CVE-2020-7053
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-14
Source: https://osv.dev/vulnerability/CVE-2020-7053
Type: osv

## Details
In the Linux kernel 4.14 longterm through 4.14.165 and 4.19 longterm through 4.19.96 (and 5.x before 5.2), there is a use-after-free (write) in the i915_ppgtt_close function in drivers/gpu/drm/i915/i915_gem_gtt.c, aka CID-7dc40713618c. This is related to i915_gem_context_destroy_ioctl in drivers/gpu/drm/i915/i915_gem_context.c.

## References
- https://usn.ubuntu.com/4287-1/
- https://usn.ubuntu.com/4287-2/
- http://packetstormsecurity.com/files/156455/Kernel-Live-Patch-Security-Notice-LSN-0063-1.html
- https://lore.kernel.org/stable/20200114183937.12224-1-tyhicks%40canonical.com
- https://usn.ubuntu.com/4255-2/
- https://usn.ubuntu.com/4285-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://usn.ubuntu.com/4255-1/
- https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1859522
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2
- https://security.netapp.com/advisory/ntap-20200204-0002/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=7dc40713618c884bf07c030d1ab1f47a9dc1f310
