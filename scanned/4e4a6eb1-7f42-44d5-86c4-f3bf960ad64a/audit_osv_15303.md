# [M] CVE-2019-15141

## Summary
Severity: Medium
Advisory: CVE-2019-15141
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-08-18
Source: https://osv.dev/vulnerability/CVE-2019-15141
Type: osv

## Details
WriteTIFFImage in coders/tiff.c in ImageMagick 7.0.8-43 Q16 allows attackers to cause a denial-of-service (application crash resulting from a heap-based buffer over-read) via a crafted TIFF image file, related to TIFFRewriteDirectory, TIFFWriteDirectory, TIFFWriteDirectorySec, and TIFFWriteDirectoryTagColormap in tif_dirwrite.c of LibTIFF. NOTE: this occurs because of an incomplete fix for CVE-2019-11597.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00040.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00042.html
- https://github.com/ImageMagick/ImageMagick/issues/1560
- https://github.com/ImageMagick/ImageMagick6/commit/3c53413eb544cc567309b4c86485eae43e956112
