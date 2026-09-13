# [H] CVE-2017-11403

## Summary
Severity: High
Advisory: CVE-2017-11403
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-18
Source: https://osv.dev/vulnerability/CVE-2017-11403
Type: osv

## Details
The ReadMNGImage function in coders/png.c in GraphicsMagick 1.3.26 has an out-of-order CloseBlob call, resulting in a use-after-free via a crafted file.

## References
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- https://usn.ubuntu.com/4206-1/
- https://www.debian.org/security/2018/dsa-4321
- http://hg.code.sf.net/p/graphicsmagick/code/rev/d0a76868ca37
- https://blogs.gentoo.org/ago/2017/07/12/graphicsmagick-use-after-free-in-closeblob-blob-c/
