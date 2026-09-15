# [H] CVE-2019-13306

## Summary
Severity: High
Advisory: CVE-2019-13306
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-05
Source: https://osv.dev/vulnerability/CVE-2019-13306
Type: osv

## Details
ImageMagick 7.0.8-50 Q16 has a stack-based buffer overflow at coders/pnm.c in WritePNMImage because of off-by-one errors.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00069.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00021.html
- https://usn.ubuntu.com/4192-1/
- https://www.debian.org/security/2020/dsa-4715
- https://github.com/ImageMagick/ImageMagick/commit/e92040ea6ee2a844ebfd2344174076795a4787bd
- https://github.com/ImageMagick/ImageMagick/issues/1612
- https://github.com/ImageMagick/ImageMagick6/commit/cb5ec7d98195aa74d5ed299b38eff2a68122f3fa
