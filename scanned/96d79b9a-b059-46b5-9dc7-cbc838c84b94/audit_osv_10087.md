# [M] CVE-2017-13145

## Summary
Severity: Medium
Advisory: CVE-2017-13145
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-23
Source: https://osv.dev/vulnerability/CVE-2017-13145
Type: osv

## Details
In ImageMagick before 6.9.8-8 and 7.x before 7.0.5-9, the ReadJP2Image function in coders/jp2.c does not properly validate the channel geometry, leading to a crash.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00015.html
- https://security.gentoo.org/glsa/201711-07
- https://usn.ubuntu.com/3681-1/
- https://www.debian.org/security/2017/dsa-4019
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=869830
- https://github.com/ImageMagick/ImageMagick/commit/acee073df34aa4d491bf5cb74d3a15fc80f0a3aa
- https://github.com/ImageMagick/ImageMagick/commit/f13c6b54a879aaa771ec64b5a066b939e8f8e7f0
- https://github.com/ImageMagick/ImageMagick/issues/501
