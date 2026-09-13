# [M] CVE-2018-7470

## Summary
Severity: Medium
Advisory: CVE-2018-7470
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-25
Source: https://osv.dev/vulnerability/CVE-2018-7470
Type: osv

## Details
An issue was discovered in ImageMagick 7.0.7-22 Q16. The IsWEBPImageLossless function in coders/webp.c allows attackers to cause a denial of service (segmentation violation) via a crafted file.

## References
- https://github.com/ImageMagick/ImageMagick/issues/998
