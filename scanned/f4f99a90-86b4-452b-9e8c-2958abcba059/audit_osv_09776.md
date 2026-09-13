# [H] CVE-2017-11450

## Summary
Severity: High
Advisory: CVE-2017-11450
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-19
Source: https://osv.dev/vulnerability/CVE-2017-11450
Type: osv

## Details
coders/jpeg.c in ImageMagick before 7.0.6-1 allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via JPEG data that is too short.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=867894
- https://github.com/ImageMagick/ImageMagick/commit/948356eec65aea91995d4b7cc487d197d2c5f602
- https://github.com/ImageMagick/ImageMagick/issues/556
- https://security-tracker.debian.org/tracker/CVE-2017-11450
