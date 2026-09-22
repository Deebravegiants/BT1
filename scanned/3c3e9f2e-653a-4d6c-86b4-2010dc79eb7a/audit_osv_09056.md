# [M] CVE-2016-7529

## Summary
Severity: Medium
Advisory: CVE-2016-7529
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-19
Source: https://osv.dev/vulnerability/CVE-2016-7529
Type: osv

## Details
coders/xcf.c in ImageMagick allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted XCF file.

## References
- http://www.securityfocus.com/bid/93131
- https://bugs.launchpad.net/ubuntu/+source/imagemagick/+bug/1539051
- https://bugs.launchpad.net/ubuntu/+source/imagemagick/+bug/1539052
- https://bugzilla.redhat.com/show_bug.cgi?id=1378761
- http://www.openwall.com/lists/oss-security/2016/09/22/2
- https://github.com/ImageMagick/ImageMagick/commit/a2e1064f288a353bc5fef7f79ccb7683759e775c
- https://github.com/ImageMagick/ImageMagick/issues/103
- https://github.com/ImageMagick/ImageMagick/issues/104
