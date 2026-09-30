# [H] CVE-2017-9098

## Summary
Severity: High
Advisory: CVE-2017-9098
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-05-19
Source: https://osv.dev/vulnerability/CVE-2017-9098
Type: osv

## Details
ImageMagick before 7.0.5-2 and GraphicsMagick before 1.3.24 use uninitialized memory in the RLE decoder, allowing an attacker to leak sensitive information from process memory space, as demonstrated by remote attacks against ImageMagick code in a long-running server process that converts image data on behalf of multiple users. This is caused by a missing initialization step in the ReadRLEImage function in coders/rle.c.

## References
- http://www.debian.org/security/2017/dsa-3863
- http://www.securityfocus.com/bid/98593
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- http://hg.code.sf.net/p/graphicsmagick/code/diff/0a5b75e019b6/coders/rle.c
- https://github.com/ImageMagick/ImageMagick/commit/1c358ffe0049f768dd49a8a889c1cbf99ac9849b
- https://scarybeastsecurity.blogspot.com/2017/05/bleed-continues-18-byte-file-14k-bounty.html
