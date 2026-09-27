# [H] CVE-2019-13307

## Summary
Severity: High
Advisory: CVE-2019-13307
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-05
Source: https://osv.dev/vulnerability/CVE-2019-13307
Type: osv

## Details
ImageMagick 7.0.8-50 Q16 has a heap-based buffer overflow at MagickCore/statistic.c in EvaluateImages because of mishandling rows.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00069.html
- https://usn.ubuntu.com/4192-1/
- https://www.debian.org/security/2020/dsa-4712
- https://www.debian.org/security/2020/dsa-4715
- https://github.com/ImageMagick/ImageMagick/commit/025e77fcb2f45b21689931ba3bf74eac153afa48
- https://github.com/ImageMagick/ImageMagick/issues/1615
- https://github.com/ImageMagick/ImageMagick6/commit/91e58d967a92250439ede038ccfb0913a81e59fe
