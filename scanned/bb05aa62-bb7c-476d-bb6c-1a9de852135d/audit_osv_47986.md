# [M] CVE-2017-16530

## Summary
Severity: Medium
Advisory: CVE-2017-16530
CVSS: 6.6 (CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-04
Source: https://osv.dev/vulnerability/CVE-2017-16530
Type: osv

## Details
The uas driver in the Linux kernel before 4.13.6 allows local users to cause a denial of service (out-of-bounds read and system crash) or possibly have unspecified other impact via a crafted USB device, related to drivers/usb/storage/uas-detect.h and drivers/usb/storage/uas.c.

## References
- https://github.com/torvalds/linux/commit/786de92b3cb26012d3d0f00ee37adf14527f35c4
- https://groups.google.com/d/msg/syzkaller/pCswO77gRlM/VHuPOftgAwAJ
