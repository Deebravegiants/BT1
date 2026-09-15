# [M] CVE-2017-11523

## Summary
Severity: Medium
Advisory: CVE-2017-11523
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-22
Source: https://osv.dev/vulnerability/CVE-2017-11523
Type: osv

## Details
The ReadTXTImage function in coders/txt.c in ImageMagick through 6.9.9-0 and 7.x through 7.0.6-1 allows remote attackers to cause a denial of service (infinite loop) via a crafted file, because the end-of-file condition is not considered.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00015.html
- https://github.com/ImageMagick/ImageMagick/commit/a8f9c2aabed37cd6a728532d1aed13ae0f3dfd78
- https://www.debian.org/security/2017/dsa-4019
- https://bugs.debian.org/869210
- https://github.com/ImageMagick/ImageMagick/commit/83e0f8ffd7eeb7661b0ff83257da23d24ca7f078
- https://github.com/ImageMagick/ImageMagick/issues/591
