# [H] CVE-2019-13300

## Summary
Severity: High
Advisory: CVE-2019-13300
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-05
Source: https://osv.dev/vulnerability/CVE-2019-13300
Type: osv

## Details
ImageMagick 7.0.8-50 Q16 has a heap-based buffer overflow at MagickCore/statistic.c in EvaluateImages because of mishandling columns.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00069.html
- https://usn.ubuntu.com/4192-1/
- https://www.debian.org/security/2020/dsa-4712
- https://www.debian.org/security/2020/dsa-4715
- https://github.com/ImageMagick/ImageMagick/commit/a906fe9298bf89e01d5272023db687935068849a
- https://github.com/ImageMagick/ImageMagick/issues/1586
- https://github.com/ImageMagick/ImageMagick6/commit/5e409ae7a389cdf2ed17469303be3f3f21cec450
