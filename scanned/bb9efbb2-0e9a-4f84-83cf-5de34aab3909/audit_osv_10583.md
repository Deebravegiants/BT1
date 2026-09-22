# [C] CVE-2017-17499

## Summary
Severity: Critical
Advisory: CVE-2017-17499
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-11
Source: https://osv.dev/vulnerability/CVE-2017-17499
Type: osv

## Details
ImageMagick before 6.9.9-24 and 7.x before 7.0.7-12 has a use-after-free in Magick::Image::read in Magick++/lib/Image.cpp.

## References
- http://www.securityfocus.com/bid/102155
- https://github.com/ImageMagick/ImageMagick/commit/dd96d671e4d5ae22c6894c302e8996c13f24c45a
- https://usn.ubuntu.com/3681-1/
- https://www.debian.org/security/2017/dsa-4074
- https://github.com/ImageMagick/ImageMagick/commit/8c35502217c1879cb8257c617007282eee3fe1cc
- https://www.imagemagick.org/discourse-server/viewtopic.php?f=3&t=33078&sid=5fbb164c3830293138917f9b14264ed1
