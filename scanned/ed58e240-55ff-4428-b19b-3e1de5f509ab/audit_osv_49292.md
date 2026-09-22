# [H] CVE-2018-9516

## Summary
Severity: High
Advisory: CVE-2018-9516
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-06
Source: https://osv.dev/vulnerability/CVE-2018-9516
Type: osv

## Details
In hid_debug_events_read of drivers/hid/hid-debug.c, there is a possible out of bounds write due to a missing bounds check. This could lead to local escalation of privilege with System execution privileges needed. User interaction is not needed for exploitation. Product: Android Versions: Android kernel Android ID: A-71361580.

## References
- https://access.redhat.com/errata/RHSA-2019:2043
- https://lists.debian.org/debian-lts-announce/2018/10/msg00003.html
- https://usn.ubuntu.com/3871-1/
- https://usn.ubuntu.com/3871-3/
- https://usn.ubuntu.com/3871-5/
- https://access.redhat.com/errata/RHSA-2019:2029
- https://usn.ubuntu.com/3871-4/
- https://www.debian.org/security/2018/dsa-4308
- https://source.android.com/security/bulletin/pixel/2018-09-01
