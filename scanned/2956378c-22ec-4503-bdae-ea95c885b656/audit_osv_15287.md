# [M] CVE-2019-14981

## Summary
Severity: Medium
Advisory: CVE-2019-14981
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-08-12
Source: https://osv.dev/vulnerability/CVE-2019-14981
Type: osv

## Details
In ImageMagick 7.x before 7.0.8-41 and 6.x before 6.9.10-41, there is a divide-by-zero vulnerability in the MeanShiftImage function. It allows an attacker to cause a denial of service by sending a crafted file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00040.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00042.html
- https://lists.debian.org/debian-lts-announce/2019/10/msg00028.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00030.html
- https://usn.ubuntu.com/4192-1/
- https://www.debian.org/security/2020/dsa-4712
- https://github.com/ImageMagick/ImageMagick/commit/a77d8d97f5a7bced0468f0b08798c83fb67427bc
- https://github.com/ImageMagick/ImageMagick/issues/1552
- https://github.com/ImageMagick/ImageMagick6/commit/b522d2d857d2f75b659936b59b0da9df1682c256
