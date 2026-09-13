# [M] CVE-2017-12675

## Summary
Severity: Medium
Advisory: CVE-2017-12675
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-07
Source: https://osv.dev/vulnerability/CVE-2017-12675
Type: osv

## Details
In ImageMagick 7.0.6-3, a missing check for multidimensional data was found in coders/mat.c, leading to a memory leak in the function ReadImage in MagickCore/constitute.c, which allows attackers to cause a denial of service.

## References
- https://github.com/ImageMagick/ImageMagick/issues/616
