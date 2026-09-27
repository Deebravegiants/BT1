# [H] CVE-2018-19824

## Summary
Severity: High
Advisory: CVE-2018-19824
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-03
Source: https://osv.dev/vulnerability/CVE-2018-19824
Type: osv

## Details
In the Linux kernel through 4.19.6, a local user could exploit a use-after-free in the ALSA driver by supplying a malicious USB Sound device (with zero interfaces) that is mishandled in usb_audio_probe in sound/usb/card.c.

## References
- https://usn.ubuntu.com/3879-2/
- https://usn.ubuntu.com/3931-2/
- https://usn.ubuntu.com/3933-1/
- https://access.redhat.com/errata/RHSA-2019:2703
- https://lists.debian.org/debian-lts-announce/2019/03/msg00034.html
- https://lists.debian.org/debian-lts-announce/2019/05/msg00002.html
- https://usn.ubuntu.com/3930-1/
- https://usn.ubuntu.com/3933-2/
- https://lists.debian.org/debian-lts-announce/2019/04/msg00004.html
- https://support.f5.com/csp/article/K98155950
- https://usn.ubuntu.com/3879-1/
- https://usn.ubuntu.com/3930-2/
- https://usn.ubuntu.com/3931-1/
- http://www.securityfocus.com/bid/106109
- https://github.com/torvalds/linux/commit/5f8cf712582617d523120df67d392059eaf2fc4b
- https://git.kernel.org/pub/scm/linux/kernel/git/tiwai/sound.git/commit/?id=5f8cf712582617d523120df67d392059eaf2fc4b
- https://bugzilla.suse.com/show_bug.cgi?id=1118152
