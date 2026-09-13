# [M] CVE-2019-9453

## Summary
Severity: Medium
Advisory: CVE-2019-9453
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-09-06
Source: https://osv.dev/vulnerability/CVE-2019-9453
Type: osv

## Details
In the Android kernel in F2FS touch driver there is a possible out of bounds read due to improper input validation. This could lead to local information disclosure with system execution privileges needed. User interaction is not needed for exploitation.

## References
- https://usn.ubuntu.com/4527-1/
- https://source.android.com/security/bulletin/pixel/2019-09-01
