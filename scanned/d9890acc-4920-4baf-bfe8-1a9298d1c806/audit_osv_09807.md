# [M] CVE-2017-11540

## Summary
Severity: Medium
Advisory: CVE-2017-11540
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-23
Source: https://osv.dev/vulnerability/CVE-2017-11540
Type: osv

## Details
When ImageMagick 7.0.6-1 processes a crafted file in convert, it can lead to a heap-based buffer over-read in the GetPixelIndex() function, called from the WritePICONImage function in coders/xpm.c.

## References
- http://www.securityfocus.com/bid/99929
- https://github.com/ImageMagick/ImageMagick/issues/581
