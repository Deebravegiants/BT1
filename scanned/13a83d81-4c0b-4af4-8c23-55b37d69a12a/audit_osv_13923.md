# [H] CVE-2018-5360

## Summary
Severity: High
Advisory: CVE-2018-5360
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-01-14
Source: https://osv.dev/vulnerability/CVE-2018-5360
Type: osv

## Details
LibTIFF before 4.0.6 mishandles the reading of TIFF files, as demonstrated by a heap-based buffer over-read in the ReadTIFFImage function in coders/tiff.c in GraphicsMagick 1.3.27.

## References
- http://bugzilla.maptools.org/show_bug.cgi?id=2500
- https://sourceforge.net/p/graphicsmagick/bugs/540/
- https://gitlab.com/libtiff/libtiff/commit/739dcd28a061738b317c1e9f91029d9cbc157159
