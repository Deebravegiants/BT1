# [M] CVE-2019-2101

## Summary
Severity: Medium
Advisory: CVE-2019-2101
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-06-07
Source: https://osv.dev/vulnerability/CVE-2019-2101
Type: osv

## Details
In uvc_parse_standard_control of uvc_driver.c, there is a possible out-of-bound read due to improper input validation. This could lead to local information disclosure with no additional execution privileges needed. User interaction is not needed for exploitation. Product: Android. Versions: Android kernel. Android ID: A-111760968.

## References
- http://packetstormsecurity.com/files/154245/Kernel-Live-Patch-Security-Notice-LSN-0054-1.html
- https://lists.debian.org/debian-lts-announce/2019/07/msg00022.html
- https://source.android.com/security/bulletin/2019-06-01
- https://usn.ubuntu.com/4094-1/
- https://usn.ubuntu.com/4118-1/
