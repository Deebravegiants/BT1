# [M] CVE-2017-7595

## Summary
Severity: Medium
Advisory: CVE-2017-7595
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-09
Source: https://osv.dev/vulnerability/CVE-2017-7595
Type: osv

## Details
The JPEGSetupEncode function in tiff_jpeg.c in LibTIFF 4.0.7 allows remote attackers to cause a denial of service (divide-by-zero error and application crash) via a crafted image.

## References
- http://www.securityfocus.com/bid/97501
- https://usn.ubuntu.com/3602-1/
- http://www.debian.org/security/2017/dsa-3844
- https://security.gentoo.org/glsa/201709-27
- https://blogs.gentoo.org/ago/2017/04/01/libtiff-divide-by-zero-in-jpegsetupencode-tiff_jpeg-c
