# [M] CVE-2017-16649

## Summary
Severity: Medium
Advisory: CVE-2017-16649
CVSS: 6.6 (CVSS:3.0/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-07
Source: https://osv.dev/vulnerability/CVE-2017-16649
Type: osv

## Details
The usbnet_generic_cdc_bind function in drivers/net/usb/cdc_ether.c in the Linux kernel through 4.13.11 allows local users to cause a denial of service (divide-by-zero error and system crash) or possibly have unspecified other impact via a crafted USB device.

## References
- https://usn.ubuntu.com/3619-2/
- https://usn.ubuntu.com/3822-1/
- https://lists.debian.org/debian-lts-announce/2017/12/msg00004.html
- https://usn.ubuntu.com/3617-3/
- https://usn.ubuntu.com/3822-2/
- https://usn.ubuntu.com/3617-1/
- https://usn.ubuntu.com/3617-2/
- https://usn.ubuntu.com/3619-1/
- https://groups.google.com/d/msg/syzkaller/0e0gmaX9R0g/9Me9JcY2BQAJ
- https://patchwork.ozlabs.org/patch/834771/
- http://www.securityfocus.com/bid/101761
