# [C] CVE-2025-27796

## Summary
Severity: Critical
Advisory: CVE-2025-27796
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-07
Source: https://osv.dev/vulnerability/CVE-2025-27796
Type: osv

## Details
ReadWPGImage in WPG in GraphicsMagick before 1.3.46 mishandles palette buffer allocation, resulting in out-of-bounds access to heap memory in ReadBlob.

## References
- http://www.graphicsmagick.org/NEWS.html
- https://sourceforge.net/p/graphicsmagick/bugs/750/
- https://foss.heptapod.net/graphicsmagick/graphicsmagick/-/commit/883ebf8cae6dfa5873d975fe3476b1a188ef3f9f
