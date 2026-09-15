# [H] CVE-2016-4568

## Summary
Severity: High
Advisory: CVE-2016-4568
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-23
Source: https://osv.dev/vulnerability/CVE-2016-4568
Type: osv

## Details
drivers/media/v4l2-core/videobuf2-v4l2.c in the Linux kernel before 4.5.3 allows local users to cause a denial of service (kernel memory write operation) or possibly have unspecified other impact via a crafted number of planes in a VIDIOC_DQBUF ioctl call.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=2c1f6951a8a82e6de0d82b1158b5e493fc6c54ab
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.5.3
- http://www.openwall.com/lists/oss-security/2016/05/07/4
- https://github.com/torvalds/linux/commit/2c1f6951a8a82e6de0d82b1158b5e493fc6c54ab
- https://bugzilla.redhat.com/show_bug.cgi?id=1334316
