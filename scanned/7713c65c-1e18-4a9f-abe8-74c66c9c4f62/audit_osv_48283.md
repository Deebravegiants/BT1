# [M] CVE-2017-5577

## Summary
Severity: Medium
Advisory: CVE-2017-5577
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-06
Source: https://osv.dev/vulnerability/CVE-2017-5577
Type: osv

## Details
The vc4_get_bcl function in drivers/gpu/drm/vc4/vc4_gem.c in the VideoCore DRM driver in the Linux kernel before 4.9.7 does not set an errno value upon certain overflow detections, which allows local users to cause a denial of service (incorrect pointer dereference and OOPS) via inconsistent size values in a VC4_SUBMIT_CL ioctl call.

## References
- http://www.securityfocus.com/bid/95765
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.7
- https://bugzilla.redhat.com/show_bug.cgi?id=1416437
- https://github.com/torvalds/linux/commit/6b8ac63847bc2f958dd93c09edc941a0118992d9
- https://lkml.org/lkml/2017/1/17/759
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6b8ac63847bc2f958dd93c09edc941a0118992d9
- http://www.openwall.com/lists/oss-security/2017/01/21/7
