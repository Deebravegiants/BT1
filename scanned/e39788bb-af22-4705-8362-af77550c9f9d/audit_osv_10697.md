# [M] CVE-2017-18272

## Summary
Severity: Medium
Advisory: CVE-2017-18272
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-18
Source: https://osv.dev/vulnerability/CVE-2017-18272
Type: osv

## Details
In ImageMagick 7.0.7-16 Q16 x86_64 2017-12-25, there is a use-after-free in ReadOneMNGImage in coders/png.c, which allows attackers to cause a denial of service via a crafted MNG image file that is mishandled in an MngInfoDiscardObject call.

## References
- https://github.com/ImageMagick/ImageMagick/issues/918
