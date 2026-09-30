# [M] CVE-2017-13769

## Summary
Severity: Medium
Advisory: CVE-2017-13769
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-30
Source: https://osv.dev/vulnerability/CVE-2017-13769
Type: osv

## Details
The WriteTHUMBNAILImage function in coders/thumbnail.c in ImageMagick through 7.0.6-10 allows an attacker to cause a denial of service (buffer over-read) by sending a crafted JPEG file.

## References
- https://security.gentoo.org/glsa/201711-07
- https://usn.ubuntu.com/3681-1/
- https://www.debian.org/security/2017/dsa-4032
- https://www.debian.org/security/2017/dsa-4040
- https://github.com/ImageMagick/ImageMagick/issues/705
