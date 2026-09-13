# [M] CVE-2016-7526

## Summary
Severity: Medium
Advisory: CVE-2016-7526
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-20
Source: https://osv.dev/vulnerability/CVE-2016-7526
Type: osv

## Details
coders/wpg.c in ImageMagick allows remote attackers to cause a denial of service (out-of-bounds write) via a crafted file.

## References
- http://www.securityfocus.com/bid/93131
- https://bugs.launchpad.net/bugs/1539050
- http://www.openwall.com/lists/oss-security/2016/09/22/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1378758
- https://github.com/ImageMagick/ImageMagick/commit/998c687fb83993c13fa711d75f59a95b38ceab77
- https://github.com/ImageMagick/ImageMagick/commit/b60d1ed0af37c50b91a40937825b4c61e8458095
- https://github.com/ImageMagick/ImageMagick/commit/b6ae2f9e0ab13343c0281732d479757a8e8979c7
- https://github.com/ImageMagick/ImageMagick/commit/d9b2209a69ee90d8df81fb124eb66f593eb9f599
- https://github.com/ImageMagick/ImageMagick/issues/102
