# [M] CVE-2020-0093

## Summary
Severity: Medium
Advisory: CVE-2020-0093
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2020-05-14
Source: https://osv.dev/vulnerability/CVE-2020-0093
Type: osv

## Details
In exif_data_save_data_entry of exif-data.c, there is a possible out of bounds read due to a missing bounds check. This could lead to local information disclosure with no additional execution privileges needed. User interaction is needed for exploitation.Product: AndroidVersions: Android-8.0 Android-8.1 Android-9 Android-10Android ID: A-148705132

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2020/05/msg00016.html
- https://usn.ubuntu.com/4396-1/
- https://security.gentoo.org/glsa/202007-05
- https://source.android.com/security/bulletin/2020-05-01
