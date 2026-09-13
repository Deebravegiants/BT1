# [M] CVE-2017-14989

## Summary
Severity: Medium
Advisory: CVE-2017-14989
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-03
Source: https://osv.dev/vulnerability/CVE-2017-14989
Type: osv

## Details
A use-after-free in RenderFreetype in MagickCore/annotate.c in ImageMagick 7.0.7-4 Q16 allows attackers to crash the application via a crafted font file, because the FT_Done_Glyph function (from FreeType 2) is called at an incorrect place in the ImageMagick code.

## References
- https://usn.ubuntu.com/3681-1/
- https://www.debian.org/security/2017/dsa-4032
- https://www.debian.org/security/2017/dsa-4040
- https://github.com/ImageMagick/ImageMagick/issues/781
