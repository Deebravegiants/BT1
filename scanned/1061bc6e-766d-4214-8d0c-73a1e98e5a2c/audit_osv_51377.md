# [M] CVE-2021-30002

## Summary
Severity: Medium
Advisory: CVE-2021-30002
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-02
Source: https://osv.dev/vulnerability/CVE-2021-30002
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.11.3 when a webcam device exists. video_usercopy in drivers/media/v4l2-core/v4l2-ioctl.c has a memory leak for large arguments, aka CID-fb18802a338b.

## References
- https://lists.debian.org/debian-lts-announce/2021/06/msg00020.html
- https://bugzilla.suse.com/show_bug.cgi?id=1184120
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.3
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=fb18802a338b36f675a388fc03d2aa504a0d0899
