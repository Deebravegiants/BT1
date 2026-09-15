# [M] CVE-2019-9454

## Summary
Severity: Medium
Advisory: CVE-2019-9454
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-06
Source: https://osv.dev/vulnerability/CVE-2019-9454
Type: osv

## Details
In the Android kernel in i2c driver there is a possible out of bounds write due to memory corruption. This could lead to local escalation of privilege with System execution privileges needed. User interaction is not needed for exploitation.

## References
- https://source.android.com/security/bulletin/pixel/2019-09-01
- https://source.android.com/security/bulletin/pixel/2019-09-01
