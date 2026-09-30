# [M] CVE-2019-2228

## Summary
Severity: Medium
Advisory: CVE-2019-2228
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-12-06
Source: https://osv.dev/vulnerability/CVE-2019-2228
Type: osv

## Details
In array_find of array.c, there is a possible out-of-bounds read due to an incorrect bounds check. This could lead to local information disclosure in the printer spooler with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android-8.0 Android-8.1 Android-9 Android-10Android ID: A-111210196

## References
- https://lists.debian.org/debian-lts-announce/2019/12/msg00030.html
- https://usn.ubuntu.com/4340-1/
- https://source.android.com/security/bulletin/2019-12-01
