# [M] CVE-2017-16644

## Summary
Severity: Medium
Advisory: CVE-2017-16644
CVSS: 6.6 (CVSS:3.0/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-07
Source: https://osv.dev/vulnerability/CVE-2017-16644
Type: osv

## Details
The hdpvr_probe function in drivers/media/usb/hdpvr/hdpvr-core.c in the Linux kernel through 4.13.11 allows local users to cause a denial of service (improper error handling and system crash) or possibly have unspecified other impact via a crafted USB device.

## References
- https://usn.ubuntu.com/3754-1/
- https://patchwork.kernel.org/patch/9966135/
- https://www.debian.org/security/2017/dsa-4073
- http://www.securityfocus.com/bid/101842
- https://groups.google.com/d/msg/syzkaller/ngC5SLvxPm4/gduhCARhAwAJ
