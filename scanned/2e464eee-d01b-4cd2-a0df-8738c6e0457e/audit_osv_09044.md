# [M] CVE-2016-7517

## Summary
Severity: Medium
Advisory: CVE-2016-7517
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-20
Source: https://osv.dev/vulnerability/CVE-2016-7517
Type: osv

## Details
The EncodeImage function in coders/pict.c in ImageMagick allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted PICT file.

## References
- http://www.securityfocus.com/bid/93128
- https://bugs.launchpad.net/ubuntu/+source/imagemagick/+bug/1533449
- http://www.openwall.com/lists/oss-security/2016/09/22/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1378744
- https://github.com/ImageMagick/ImageMagick/issues/80
