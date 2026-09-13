# [M] CVE-2017-14173

## Summary
Severity: Medium
Advisory: CVE-2017-14173
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-07
Source: https://osv.dev/vulnerability/CVE-2017-14173
Type: osv

## Details
In the function ReadTXTImage() in coders/txt.c in ImageMagick 7.0.6-10, an integer overflow might occur for the addition operation "GetQuantumRange(depth)+1" when "depth" is large, producing a smaller value than expected. As a result, an infinite loop would occur for a crafted TXT file that claims a very large "max_value" value.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00015.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00007.html
- https://security.gentoo.org/glsa/201711-07
- https://usn.ubuntu.com/3681-1/
- https://github.com/ImageMagick/ImageMagick/commit/50f54462076648ac2e36c3f58f4dadd4babbf1c9
- https://github.com/ImageMagick/ImageMagick/issues/713
