# [M] CVE-2017-16527

## Summary
Severity: Medium
Advisory: CVE-2017-16527
CVSS: 6.6 (CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-04
Source: https://osv.dev/vulnerability/CVE-2017-16527
Type: osv

## Details
sound/usb/mixer.c in the Linux kernel before 4.13.8 allows local users to cause a denial of service (snd_usb_mixer_interrupt use-after-free and system crash) or possibly have unspecified other impact via a crafted USB device.

## References
- https://groups.google.com/d/msg/syzkaller/jf7GTr_g2CU/iVlLhMciCQAJ
- https://lists.debian.org/debian-lts-announce/2017/12/msg00004.html
- https://usn.ubuntu.com/3754-1/
- https://github.com/torvalds/linux/commit/124751d5e63c823092060074bd0abaae61aaa9c4
