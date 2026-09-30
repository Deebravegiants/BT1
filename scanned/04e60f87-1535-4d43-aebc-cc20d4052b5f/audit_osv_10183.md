# [M] CVE-2017-14172

## Summary
Severity: Medium
Advisory: CVE-2017-14172
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-07
Source: https://osv.dev/vulnerability/CVE-2017-14172
Type: osv

## Details
In coders/ps.c in ImageMagick 7.0.7-0 Q16, a DoS in ReadPSImage() due to lack of an EOF (End of File) check might cause huge CPU consumption. When a crafted PSD file, which claims a large "extent" field in the header but does not contain sufficient backing data, is provided, the loop over "length" would consume huge CPU resources, since there is no EOF check inside the loop.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00015.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00007.html
- https://security.gentoo.org/glsa/201711-07
- https://usn.ubuntu.com/3681-1/
- https://github.com/ImageMagick/ImageMagick/commit/bdbbb13f1fe9b7e2465502c500561720f7456aac
- https://github.com/ImageMagick/ImageMagick/issues/715
