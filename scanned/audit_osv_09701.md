# [H] CVE-2017-10928

## Summary
Severity: High
Advisory: CVE-2017-10928
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-05
Source: https://osv.dev/vulnerability/CVE-2017-10928
Type: osv

## Details
In ImageMagick 7.0.6-0, a heap-based buffer over-read in the GetNextToken function in token.c allows remote attackers to obtain sensitive information from process memory or possibly have unspecified other impact via a crafted SVG document that is mishandled in the GetUserSpaceCoordinateValue function in coders/svg.c.

## References
- http://www.securityfocus.com/bid/99480
- https://github.com/ImageMagick/ImageMagick/issues/539
