# [M] CVE-2017-8765

## Summary
Severity: Medium
Advisory: CVE-2017-8765
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-04
Source: https://osv.dev/vulnerability/CVE-2017-8765
Type: osv

## Details
The function named ReadICONImage in coders\icon.c in ImageMagick 7.0.5-5 has a memory leak vulnerability which can cause memory exhaustion via a crafted ICON file.

## References
- http://www.securityfocus.com/bid/98688
- http://www.debian.org/security/2017/dsa-3863
- https://github.com/ImageMagick/ImageMagick/issues/466
