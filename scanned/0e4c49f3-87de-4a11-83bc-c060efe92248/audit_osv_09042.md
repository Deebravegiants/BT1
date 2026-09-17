# [M] CVE-2016-7515

## Summary
Severity: Medium
Advisory: CVE-2016-7515
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-19
Source: https://osv.dev/vulnerability/CVE-2016-7515
Type: osv

## Details
The ReadRLEImage function in coders/rle.c in ImageMagick allows remote attackers to cause a denial of service (out-of-bounds read) via vectors related to the number of pixels.

## References
- http://www.securityfocus.com/bid/93120
- https://bugs.launchpad.net/ubuntu/+source/imagemagick/+bug/1533445
- https://bugzilla.redhat.com/show_bug.cgi?id=1378741
- http://www.openwall.com/lists/oss-security/2016/09/22/2
- https://github.com/ImageMagick/ImageMagick/commit/2ad6d33493750a28a5a655d319a8e0b16c392de1
- https://github.com/ImageMagick/ImageMagick/issues/82
