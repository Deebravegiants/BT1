# [M] CVE-2022-20011

## Summary
Severity: Medium
Advisory: CVE-2022-20011
Aliases: A-214999128, ASB-A-214999128
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-05-10
Source: https://osv.dev/vulnerability/CVE-2022-20011
Type: osv

## Details
In getArray of NotificationManagerService.java , there is a possible leak of one user notifications to another due to missing check. This could lead to local information disclosure with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android-10 Android-11 Android-12 Android-12LAndroid ID: A-214999128

## References
- https://source.android.com/security/bulletin/2022-05-01
