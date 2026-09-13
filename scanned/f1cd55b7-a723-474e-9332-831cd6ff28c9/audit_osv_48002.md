# [M] CVE-2017-16647

## Summary
Severity: Medium
Advisory: CVE-2017-16647
CVSS: 6.6 (CVSS:3.0/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-07
Source: https://osv.dev/vulnerability/CVE-2017-16647
Type: osv

## Details
drivers/net/usb/asix_devices.c in the Linux kernel through 4.13.11 allows local users to cause a denial of service (NULL pointer dereference and system crash) or possibly have unspecified other impact via a crafted USB device.

## References
- https://usn.ubuntu.com/3617-1/
- https://usn.ubuntu.com/3617-2/
- https://usn.ubuntu.com/3617-3/
- http://www.securityfocus.com/bid/101767
- https://groups.google.com/d/msg/syzkaller/_9a6pd-p_0E/OnmnplQuAgAJ
- https://patchwork.ozlabs.org/patch/834686/
