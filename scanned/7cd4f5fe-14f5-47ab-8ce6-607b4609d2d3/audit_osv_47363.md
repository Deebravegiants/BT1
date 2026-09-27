# [H] CVE-2016-3822

## Summary
Severity: High
Advisory: CVE-2016-3822
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-08-05
Source: https://osv.dev/vulnerability/CVE-2016-3822
Type: osv

## Details
exif.c in Matthias Wandel jhead 2.87, as used in libjhead in Android 4.x before 4.4.4, 5.0.x before 5.0.2, 5.1.x before 5.1.1, and 6.x before 2016-08-01, allows remote attackers to execute arbitrary code or cause a denial of service (out-of-bounds access) via crafted EXIF data, aka internal bug 28868315.

## References
- http://source.android.com/security/bulletin/2016-08-01.html
- http://www.debian.org/security/2017/dsa-3825
- http://www.securityfocus.com/bid/92226
- https://android.googlesource.com/platform/external/jhead/+/bae671597d47b9e5955c4cb742e468cebfd7ca6b
