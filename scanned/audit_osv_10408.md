# [M] CVE-2017-15277

## Summary
Severity: Medium
Advisory: CVE-2017-15277
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2017-10-12
Source: https://osv.dev/vulnerability/CVE-2017-15277
Type: osv

## Details
ReadGIFImage in coders/gif.c in ImageMagick 7.0.6-1 and GraphicsMagick 1.3.26 leaves the palette uninitialized when processing a GIF file that has neither a global nor local palette. If the affected product is used as a library loaded into a process that operates on interesting data, this data sometimes can be leaked via the uninitialized palette.

## References
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- https://usn.ubuntu.com/3681-1/
- https://usn.ubuntu.com/4232-1/
- https://www.debian.org/security/2017/dsa-4032
- https://www.debian.org/security/2017/dsa-4040
- https://www.debian.org/security/2018/dsa-4321
- https://github.com/ImageMagick/ImageMagick/commit/9fd10cf630832b36a588c1545d8736539b2f1fb5
- https://github.com/ImageMagick/ImageMagick/issues/592
- https://github.com/neex/gifoeb
