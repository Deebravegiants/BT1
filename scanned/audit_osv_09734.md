# [H] CVE-2017-11170

## Summary
Severity: High
Advisory: CVE-2017-11170
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-11
Source: https://osv.dev/vulnerability/CVE-2017-11170
Type: osv

## Details
The ReadTGAImage function in coders\tga.c in ImageMagick 7.0.5-6 has a memory leak vulnerability that can cause memory exhaustion via invalid colors data in the header of a TGA or VST file.

## References
- http://www.securityfocus.com/bid/99565
- https://github.com/ImageMagick/ImageMagick/issues/472
