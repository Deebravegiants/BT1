# [H] CVE-2017-17880

## Summary
Severity: High
Advisory: CVE-2017-17880
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17880
Type: osv

## Details
In ImageMagick 7.0.7-16 Q16 x86_64 2017-12-21, there is a stack-based buffer over-read in WriteWEBPImage in coders/webp.c, related to a WEBP_DECODER_ABI_VERSION check.

## References
- http://www.securityfocus.com/bid/102317
- https://github.com/ImageMagick/ImageMagick/issues/907
