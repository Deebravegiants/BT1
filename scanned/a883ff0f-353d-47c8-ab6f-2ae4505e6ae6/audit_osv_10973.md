# [M] CVE-2017-5508

## Summary
Severity: Medium
Advisory: CVE-2017-5508
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-24
Source: https://osv.dev/vulnerability/CVE-2017-5508
Type: osv

## Details
Heap-based buffer overflow in the PushQuantumPixel function in ImageMagick before 6.9.7-3 and 7.x before 7.0.4-3 allows remote attackers to cause a denial of service (application crash) via a crafted TIFF file.

## References
- http://www.debian.org/security/2017/dsa-3799
- http://www.securityfocus.com/bid/95748
- https://github.com/ImageMagick/ImageMagick/blob/6.9.7-3/ChangeLog
- https://github.com/ImageMagick/ImageMagick/blob/7.0.4-3/ChangeLog
- https://security.gentoo.org/glsa/201702-09
- https://www.imagemagick.org/discourse-server/viewtopic.php?f=3&t=31161
- http://www.openwall.com/lists/oss-security/2017/01/16/6
- http://www.openwall.com/lists/oss-security/2017/01/17/5
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=851381
- https://github.com/ImageMagick/ImageMagick/commit/c073a7712d82476b5fbee74856c46b88af9c3175
