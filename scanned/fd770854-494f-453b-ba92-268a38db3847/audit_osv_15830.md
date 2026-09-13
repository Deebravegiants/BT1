# [C] CVE-2019-19949

## Summary
Severity: Critical
Advisory: CVE-2019-19949
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-12-24
Source: https://osv.dev/vulnerability/CVE-2019-19949
Type: osv

## Details
In ImageMagick 7.0.8-43 Q16, there is a heap-based buffer over-read in the function WritePNGImage of coders/png.c, related to Magick_png_write_raw_profile and LocaleNCompare.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00006.html
- https://lists.debian.org/debian-lts-announce/2019/12/msg00033.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00030.html
- https://usn.ubuntu.com/4549-1/
- https://www.debian.org/security/2020/dsa-4712
- https://github.com/ImageMagick/ImageMagick/issues/1561
