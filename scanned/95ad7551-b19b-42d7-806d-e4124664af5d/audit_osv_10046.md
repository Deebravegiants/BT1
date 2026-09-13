# [M] CVE-2017-12877

## Summary
Severity: Medium
Advisory: CVE-2017-12877
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-28
Source: https://osv.dev/vulnerability/CVE-2017-12877
Type: osv

## Details
Use-after-free vulnerability in the DestroyImage function in image.c in ImageMagick before 7.0.6-6 allows remote attackers to cause a denial of service via a crafted file.

## References
- https://security.gentoo.org/glsa/201711-07
- https://usn.ubuntu.com/3681-1/
- https://www.debian.org/security/2017/dsa-4040
- https://www.debian.org/security/2017/dsa-4074
- http://www.openwall.com/lists/oss-security/2017/08/16/2
- https://blogs.gentoo.org/ago/2017/08/10/imagemagick-use-after-free-in-destroyimage-image-c/
- https://github.com/ImageMagick/ImageMagick/commit/04178de2247e353fc095846784b9a10fefdbf890
