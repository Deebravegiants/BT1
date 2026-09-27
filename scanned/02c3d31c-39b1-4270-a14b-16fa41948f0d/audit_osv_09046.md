# [M] CVE-2016-7519

## Summary
Severity: Medium
Advisory: CVE-2016-7519
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-19
Source: https://osv.dev/vulnerability/CVE-2016-7519
Type: osv

## Details
The ReadRLEImage function in coders/rle.c in ImageMagick allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted file.

## References
- http://www.securityfocus.com/bid/93131
- https://bugs.launchpad.net/ubuntu/+source/imagemagick/+bug/1533445
- https://bugzilla.redhat.com/show_bug.cgi?id=1378746
- http://www.openwall.com/lists/oss-security/2016/09/22/2
- https://github.com/ImageMagick/ImageMagick/issues/82
