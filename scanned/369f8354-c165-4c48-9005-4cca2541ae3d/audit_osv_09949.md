# [M] CVE-2017-12427

## Summary
Severity: Medium
Advisory: CVE-2017-12427
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-04
Source: https://osv.dev/vulnerability/CVE-2017-12427
Type: osv

## Details
The ProcessMSLScript function in coders/msl.c in ImageMagick before 6.9.9-5 and 7.x before 7.0.6-5 allows remote attackers to cause a denial of service (memory leak) via a crafted file, related to the WriteMSLImage function.

## References
- https://security.gentoo.org/glsa/201711-07
- https://github.com/ImageMagick/ImageMagick/commit/e793eb203e5e0f91f5037aed6585e81b1e27395b
- https://github.com/ImageMagick/ImageMagick/issues/636
