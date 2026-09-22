# [M] CVE-2017-16536

## Summary
Severity: Medium
Advisory: CVE-2017-16536
CVSS: 6.6 (CVSS:3.0/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-04
Source: https://osv.dev/vulnerability/CVE-2017-16536
Type: osv

## Details
The cx231xx_usb_probe function in drivers/media/usb/cx231xx/cx231xx-cards.c in the Linux kernel through 4.13.11 allows local users to cause a denial of service (NULL pointer dereference and system crash) or possibly have unspecified other impact via a crafted USB device.

## References
- https://lists.debian.org/debian-lts-announce/2017/12/msg00004.html
- https://usn.ubuntu.com/3619-1/
- https://usn.ubuntu.com/3619-2/
- https://usn.ubuntu.com/3754-1/
- https://groups.google.com/d/msg/syzkaller/WlUAVfDvpRk/1V1xuEA4AgAJ
- https://patchwork.kernel.org/patch/9963527/
