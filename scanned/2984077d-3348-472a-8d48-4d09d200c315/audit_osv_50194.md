# [M] CVE-2019-9245

## Summary
Severity: Medium
Advisory: CVE-2019-9245
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-09-06
Source: https://osv.dev/vulnerability/CVE-2019-9245
Type: osv

## Details
In the Android kernel in the f2fs driver there is a possible out of bounds read due to a missing bounds check. This could lead to local information disclosure with System execution privileges needed. User interaction is not needed for exploitation.

## References
- https://source.android.com/security/bulletin/pixel/2019-09-01
