# [M] CVE-2017-6499

## Summary
Severity: Medium
Advisory: CVE-2017-6499
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-06
Source: https://osv.dev/vulnerability/CVE-2017-6499
Type: osv

## Details
An issue was discovered in Magick++ in ImageMagick 6.9.7. A specially crafted file creating a nested exception could lead to a memory leak (thus, a DoS).

## References
- http://www.debian.org/security/2017/dsa-3808
- http://www.securityfocus.com/bid/96590
- https://bugs.debian.org/856880
- https://github.com/ImageMagick/ImageMagick/commit/3358f060fc182551822576b2c0a8850faab5d543
- https://www.imagemagick.org/discourse-server/viewtopic.php?f=23&p=142634
