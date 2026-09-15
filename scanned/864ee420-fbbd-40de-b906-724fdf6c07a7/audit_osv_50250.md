# [M] CVE-2020-0182

## Summary
Severity: Medium
Advisory: CVE-2020-0182
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2020-06-11
Source: https://osv.dev/vulnerability/CVE-2020-0182
Type: osv

## Details
In exif_entry_get_value of exif-entry.c, there is a possible out of bounds read due to a missing bounds check. This could lead to local information disclosure with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android-10Android ID: A-147140917

## References
- https://usn.ubuntu.com/4396-1/
- https://lists.debian.org/debian-lts-announce/2020/06/msg00020.html
- https://source.android.com/security/bulletin/pixel/2020-06-01
