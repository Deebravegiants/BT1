# [M] CVE-2019-2180

## Summary
Severity: Medium
Advisory: CVE-2019-2180
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-09-05
Source: https://osv.dev/vulnerability/CVE-2019-2180
Type: osv

## Details
In ippSetValueTag of ipp.c in Android 8.0, 8.1 and 9, there is a possible out of bounds read due to improper input validation. This could lead to local information disclosure from the printer service with no additional execution privileges needed. User interaction is not needed for exploitation.

## References
- https://source.android.com/security/bulletin/2019-09-01
