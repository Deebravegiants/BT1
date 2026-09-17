# [H] CVE-2017-5576

## Summary
Severity: High
Advisory: CVE-2017-5576
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-06
Source: https://osv.dev/vulnerability/CVE-2017-5576
Type: osv

## Details
Integer overflow in the vc4_get_bcl function in drivers/gpu/drm/vc4/vc4_gem.c in the VideoCore DRM driver in the Linux kernel before 4.9.7 allows local users to cause a denial of service or possibly have unspecified other impact via a crafted size value in a VC4_SUBMIT_CL ioctl call.

## References
- http://www.securityfocus.com/bid/95767
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.7
- https://bugzilla.redhat.com/show_bug.cgi?id=1416436
- https://github.com/torvalds/linux/commit/0f2ff82e11c86c05d051cae32b58226392d33bbf
- https://lkml.org/lkml/2017/1/17/761
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=0f2ff82e11c86c05d051cae32b58226392d33bbf
- http://www.openwall.com/lists/oss-security/2017/01/21/7
