# [M] CVE-2019-9444

## Summary
Severity: Medium
Advisory: CVE-2019-9444
CVSS: 4.4 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-09-06
Source: https://osv.dev/vulnerability/CVE-2019-9444
Type: osv

## Details
In the Android kernel in sync debug fs driver there is a kernel pointer leak due to the usage of printf with %p. This could lead to local information disclosure with system execution privileges needed. User interaction is not needed for exploitation.

## References
- https://source.android.com/security/bulletin/pixel/2019-09-01
