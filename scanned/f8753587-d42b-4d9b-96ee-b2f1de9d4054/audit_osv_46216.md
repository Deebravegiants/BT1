# [M] JLSEC-2026-825

## Summary
Severity: Medium
Advisory: JLSEC-2026-825
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-825
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+0

## Details
In `coders/bmp.c` in ImageMagick before 7.0.8-16, an input file can result in an infinite loop and hang, with high CPU and memory consumption. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00034.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00034.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00006.html
- http://www.securityfocus.com/bid/106315
- http://www.securityfocus.com/bid/106315
- https://github.com/ImageMagick/ImageMagick/commit/db0add932fb850d762b02604ca3053b7d7ab6deb
- https://github.com/ImageMagick/ImageMagick/commit/db0add932fb850d762b02604ca3053b7d7ab6deb
- https://github.com/ImageMagick/ImageMagick/issues/1408
- https://github.com/ImageMagick/ImageMagick/issues/1408
- https://lists.debian.org/debian-lts-announce/2020/08/msg00030.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00030.html
- https://usn.ubuntu.com/4034-1/
- https://usn.ubuntu.com/4034-1/
