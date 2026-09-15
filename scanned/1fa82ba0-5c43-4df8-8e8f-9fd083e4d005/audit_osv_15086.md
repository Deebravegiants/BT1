# [H] CVE-2019-13305

## Summary
Severity: High
Advisory: CVE-2019-13305
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-05
Source: https://osv.dev/vulnerability/CVE-2019-13305
Type: osv

## Details
ImageMagick 7.0.8-50 Q16 has a stack-based buffer overflow at coders/pnm.c in WritePNMImage because of a misplaced strncpy and an off-by-one error.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00069.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00021.html
- https://usn.ubuntu.com/4192-1/
- https://www.debian.org/security/2020/dsa-4712
- https://www.debian.org/security/2020/dsa-4715
- https://github.com/ImageMagick/ImageMagick/commit/29efd648f38b73a64d73f14cd2019d869a585888
- https://github.com/ImageMagick/ImageMagick/issues/1613
- https://github.com/ImageMagick/ImageMagick6/commit/5c7fbf9a14fb83c9685ad69d48899f490a37609d
