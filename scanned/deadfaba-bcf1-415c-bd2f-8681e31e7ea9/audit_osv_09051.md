# [M] CVE-2016-7524

## Summary
Severity: Medium
Advisory: CVE-2016-7524
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-02-06
Source: https://osv.dev/vulnerability/CVE-2016-7524
Type: osv

## Details
coders/meta.c in ImageMagick allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted file.

## References
- http://www.openwall.com/lists/oss-security/2016/09/22/2
- https://github.com/ImageMagick/ImageMagick/issues/96
- https://bugzilla.redhat.com/show_bug.cgi?id=1378762
- https://github.com/ImageMagick/ImageMagick/commit/97c9f438a9b3454d085895f4d1f66389fd22a0fb
- https://github.com/ImageMagick/ImageMagick/commit/f8c318d462270b03e77f082e2a3a32867cacd3c6
- https://bugs.launchpad.net/ubuntu/+source/imagemagick/+bug/1537422
