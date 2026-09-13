# [H] CVE-2019-13297

## Summary
Severity: High
Advisory: CVE-2019-13297
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-05
Source: https://osv.dev/vulnerability/CVE-2019-13297
Type: osv

## Details
ImageMagick 7.0.8-50 Q16 has a heap-based buffer over-read at MagickCore/threshold.c in AdaptiveThresholdImage because a height of zero is mishandled.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00069.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00021.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00030.html
- https://usn.ubuntu.com/4192-1/
- https://www.debian.org/security/2020/dsa-4712
- https://github.com/ImageMagick/ImageMagick/commit/604588fc35c7585abb7a9e71f69bb82e4389fefc
- https://github.com/ImageMagick/ImageMagick/issues/1609
- https://github.com/ImageMagick/ImageMagick6/commit/35c7032723d85eee7318ff6c82f031fa2666b773
