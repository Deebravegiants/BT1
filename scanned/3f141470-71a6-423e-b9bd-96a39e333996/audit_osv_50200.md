# [M] CVE-2019-9445

## Summary
Severity: Medium
Advisory: CVE-2019-9445
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-09-06
Source: https://osv.dev/vulnerability/CVE-2019-9445
Type: osv

## Details
In the Android kernel in F2FS driver there is a possible out of bounds read due to a missing bounds check. This could lead to local information disclosure with system execution privileges needed. User interaction is not needed for exploitation.

## References
- https://lists.debian.org/debian-lts-announce/2020/10/msg00032.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00034.html
- https://source.android.com/security/bulletin/pixel/2019-09-01
- https://usn.ubuntu.com/4526-1/
- https://usn.ubuntu.com/4527-1/
