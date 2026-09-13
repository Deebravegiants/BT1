# [M] CVE-2018-20467

## Summary
Severity: Medium
Advisory: CVE-2018-20467
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-26
Source: https://osv.dev/vulnerability/CVE-2018-20467
Type: osv

## Details
In coders/bmp.c in ImageMagick before 7.0.8-16, an input file can result in an infinite loop and hang, with high CPU and memory consumption. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00034.html
- http://www.securityfocus.com/bid/106315
- https://lists.debian.org/debian-lts-announce/2020/08/msg00030.html
- https://usn.ubuntu.com/4034-1/
- https://github.com/ImageMagick/ImageMagick/commit/db0add932fb850d762b02604ca3053b7d7ab6deb
- https://github.com/ImageMagick/ImageMagick/issues/1408
