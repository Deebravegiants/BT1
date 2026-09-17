# [M] CVE-2017-16645

## Summary
Severity: Medium
Advisory: CVE-2017-16645
CVSS: 6.6 (CVSS:3.0/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-07
Source: https://osv.dev/vulnerability/CVE-2017-16645
Type: osv

## Details
The ims_pcu_get_cdc_union_desc function in drivers/input/misc/ims-pcu.c in the Linux kernel through 4.13.11 allows local users to cause a denial of service (ims_pcu_parse_cdc_data out-of-bounds read and system crash) or possibly have unspecified other impact via a crafted USB device.

## References
- https://usn.ubuntu.com/3617-1/
- https://usn.ubuntu.com/3617-2/
- https://usn.ubuntu.com/3617-3/
- https://usn.ubuntu.com/3619-1/
- https://usn.ubuntu.com/3619-2/
- https://usn.ubuntu.com/3754-1/
- https://groups.google.com/d/msg/syzkaller/q6jjr1OhqO8/WcA99AVFBAAJ
- http://www.securityfocus.com/bid/101768
- https://github.com/torvalds/linux/commit/ea04efee7635c9120d015dcdeeeb6988130cb67a
