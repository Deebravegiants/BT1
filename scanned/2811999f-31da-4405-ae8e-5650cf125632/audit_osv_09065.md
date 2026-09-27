# [M] CVE-2016-7538

## Summary
Severity: Medium
Advisory: CVE-2016-7538
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-20
Source: https://osv.dev/vulnerability/CVE-2016-7538
Type: osv

## Details
coders/psd.c in ImageMagick allows remote attackers to cause a denial of service (out-of-bounds write) via a crafted file.

## References
- http://www.securityfocus.com/bid/93131
- https://bugs.launchpad.net/ubuntu/+source/imagemagick/+bug/1556273
- http://www.openwall.com/lists/oss-security/2016/09/22/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1378775
- https://github.com/ImageMagick/ImageMagick/commit/82e2049862a8b8a999e160734ad64fb6cc3b145f
- https://github.com/ImageMagick/ImageMagick/issues/148
