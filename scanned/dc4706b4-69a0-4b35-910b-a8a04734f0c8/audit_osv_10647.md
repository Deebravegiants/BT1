# [M] CVE-2017-17887

## Summary
Severity: Medium
Advisory: CVE-2017-17887
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17887
Type: osv

## Details
In ImageMagick 7.0.7-16 Q16, a memory leak vulnerability was found in the function GetImagePixelCache in magick/cache.c, which allows attackers to cause a denial of service via a crafted MNG image file that is processed by ReadOneMNGImage.

## References
- https://usn.ubuntu.com/3681-1/
- https://github.com/ImageMagick/ImageMagick/issues/903
