# [H] CVE-2017-16546

## Summary
Severity: High
Advisory: CVE-2017-16546
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-11-05
Source: https://osv.dev/vulnerability/CVE-2017-16546
Type: osv

## Details
The ReadWPGImage function in coders/wpg.c in ImageMagick 7.0.7-9 does not properly validate the colormap index in a WPG palette, which allows remote attackers to cause a denial of service (use of uninitialized data or invalid memory allocation) or possibly have unspecified other impact via a malformed WPG file.

## References
- https://usn.ubuntu.com/3681-1/
- https://www.debian.org/security/2017/dsa-4040
- https://www.debian.org/security/2017/dsa-4074
- https://github.com/ImageMagick/ImageMagick/commit/e04cf3e9524f50ca336253513d977224e083b816
- https://github.com/ImageMagick/ImageMagick/commit/2130bf6f89ded32ef0c88a11694f107c52566c53
- https://github.com/ImageMagick/ImageMagick/issues/851
