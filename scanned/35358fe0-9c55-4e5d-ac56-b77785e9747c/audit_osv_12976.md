# [M] CVE-2018-16644

## Summary
Severity: Medium
Advisory: CVE-2018-16644
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-06
Source: https://osv.dev/vulnerability/CVE-2018-16644
Type: osv

## Details
There is a missing check for length in the functions ReadDCMImage of coders/dcm.c and ReadPICTImage of coders/pict.c in ImageMagick 7.0.8-11, which allows remote attackers to cause a denial of service via a crafted image.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00006.html
- https://usn.ubuntu.com/4034-1/
- https://lists.debian.org/debian-lts-announce/2018/10/msg00002.html
- https://usn.ubuntu.com/3785-1/
- https://www.debian.org/security/2018/dsa-4316
- https://github.com/ImageMagick/ImageMagick/commit/16916c8979c32765c542e216b31cee2671b7afe7
- https://github.com/ImageMagick/ImageMagick/commit/afa878a689870c28b6994ecf3bb8dbfb2b76d135
- https://github.com/ImageMagick/ImageMagick/issues/1269
