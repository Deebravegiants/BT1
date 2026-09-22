# [M] CVE-2017-16646

## Summary
Severity: Medium
Advisory: CVE-2017-16646
CVSS: 6.6 (CVSS:3.0/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-07
Source: https://osv.dev/vulnerability/CVE-2017-16646
Type: osv

## Details
drivers/media/usb/dvb-usb/dib0700_devices.c in the Linux kernel through 4.13.11 allows local users to cause a denial of service (BUG and system crash) or possibly have unspecified other impact via a crafted USB device.

## References
- https://usn.ubuntu.com/3617-2/
- https://usn.ubuntu.com/3617-3/
- https://usn.ubuntu.com/3619-1/
- https://usn.ubuntu.com/3619-2/
- https://usn.ubuntu.com/3617-1/
- http://www.securityfocus.com/bid/101846
- https://groups.google.com/d/msg/syzkaller/-d6ilzbVu_g/OBy8_62mAwAJ
- https://patchwork.linuxtv.org/patch/45291/
