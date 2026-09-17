# [M] CVE-2017-7606

## Summary
Severity: Medium
Advisory: CVE-2017-7606
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-09
Source: https://osv.dev/vulnerability/CVE-2017-7606
Type: osv

## Details
coders/rle.c in ImageMagick 7.0.5-4 has an "outside the range of representable values of type unsigned char" undefined behavior issue, which might allow remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted image.

## References
- http://www.securityfocus.com/bid/98685
- http://www.debian.org/security/2017/dsa-3863
- https://blogs.gentoo.org/ago/2017/04/02/imagemagick-undefined-behavior-in-codersrle-c/
