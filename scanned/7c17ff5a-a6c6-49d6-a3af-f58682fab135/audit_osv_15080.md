# [H] CVE-2019-13295

## Summary
Severity: High
Advisory: CVE-2019-13295
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-05
Source: https://osv.dev/vulnerability/CVE-2019-13295
Type: osv

## Details
ImageMagick 7.0.8-50 Q16 has a heap-based buffer over-read at MagickCore/threshold.c in AdaptiveThresholdImage because a width of zero is mishandled.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00069.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00021.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00030.html
- https://usn.ubuntu.com/4192-1/
- https://www.debian.org/security/2020/dsa-4712
- https://github.com/ImageMagick/ImageMagick/commit/a7759f410b773a1dd57b0e1fb28112e1cd8b97bc
- https://github.com/ImageMagick/ImageMagick/issues/1608
- https://github.com/ImageMagick/ImageMagick6/commit/55e6dc49f1a381d9d511ee2f888fdc3e3c3e3953
