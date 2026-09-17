# [H] CVE-2019-12979

## Summary
Severity: High
Advisory: CVE-2019-12979
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-06-26
Source: https://osv.dev/vulnerability/CVE-2019-12979
Type: osv

## Details
ImageMagick 7.0.8-34 has a "use of uninitialized value" vulnerability in the SyncImageSettings function in MagickCore/image.c. This is related to AcquireImage in magick/image.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00069.html
- http://www.securityfocus.com/bid/108913
- https://lists.debian.org/debian-lts-announce/2020/08/msg00030.html
- https://usn.ubuntu.com/4192-1/
- https://www.debian.org/security/2020/dsa-4712
- https://github.com/ImageMagick/ImageMagick/issues/1522
