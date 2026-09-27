# [M] CVE-2018-18544

## Summary
Severity: Medium
Advisory: CVE-2018-18544
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-21
Source: https://osv.dev/vulnerability/CVE-2018-18544
Type: osv

## Details
There is a memory leak in the function WriteMSLImage of coders/msl.c in ImageMagick 7.0.8-13 Q16, and the function ProcessMSLScript of coders/msl.c in GraphicsMagick before 1.3.31.

## References
- https://usn.ubuntu.com/4034-1/
- http://hg.code.sf.net/p/graphicsmagick/code/file/233618f8fe82/ChangeLog
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00034.html
- https://github.com/ImageMagick/ImageMagick/issues/1360
