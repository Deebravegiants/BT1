# [M] CVE-2017-11360

## Summary
Severity: Medium
Advisory: CVE-2017-11360
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2017-11360
Type: osv

## Details
The ReadRLEImage function in coders\rle.c in ImageMagick 7.0.6-1 has a large loop vulnerability via a crafted rle file that triggers a huge number_pixels value.

## References
- https://github.com/ImageMagick/ImageMagick/issues/518
