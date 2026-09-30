# [H] CVE-2015-8895

## Summary
Severity: High
Advisory: CVE-2015-8895
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2015-8895
Type: osv

## Details
Integer overflow in coders/icon.c in ImageMagick 6.9.1-3 and later allows remote attackers to cause a denial of service (application crash) via a crafted length value, which triggers a buffer overflow.

## References
- http://www.openwall.com/lists/oss-security/2016/06/02/13
- http://www.securityfocus.com/bid/91025
- https://access.redhat.com/errata/RHSA-2016:1237
- https://github.com/ImageMagick/ImageMagick/commit/0f6fc2d5bf8f500820c3dbcf0d23ee14f2d9f734
- http://www.openwall.com/lists/oss-security/2016/06/02/13
- http://www.openwall.com/lists/oss-security/2016/06/02/13
- https://github.com/ImageMagick/ImageMagick/commit/0f6fc2d5bf8f500820c3dbcf0d23ee14f2d9f734
- https://bugs.launchpad.net/ubuntu/+source/imagemagick/+bug/1459747
- https://github.com/ImageMagick/ImageMagick/commit/0f6fc2d5bf8f500820c3dbcf0d23ee14f2d9f734
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
