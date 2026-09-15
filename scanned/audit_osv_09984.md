# [M] CVE-2017-12566

## Summary
Severity: Medium
Advisory: CVE-2017-12566
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-05
Source: https://osv.dev/vulnerability/CVE-2017-12566
Type: osv

## Details
In ImageMagick 7.0.6-2, a memory leak vulnerability was found in the function ReadMVGImage in coders/mvg.c, which allows attackers to cause a denial of service, related to the function ReadSVGImage in svg.c.

## References
- https://github.com/ImageMagick/ImageMagick/issues/603
