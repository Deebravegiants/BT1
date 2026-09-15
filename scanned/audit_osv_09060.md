# [M] CVE-2016-7533

## Summary
Severity: Medium
Advisory: CVE-2016-7533
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-19
Source: https://osv.dev/vulnerability/CVE-2016-7533
Type: osv

## Details
The ReadWPGImage function in coders/wpg.c in ImageMagick allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted WPG file.

## References
- http://www.securityfocus.com/bid/93131
- https://bugs.launchpad.net/ubuntu/+source/imagemagick/+bug/1542114
- https://bugzilla.redhat.com/show_bug.cgi?id=1378765
- https://github.com/ImageMagick/ImageMagick/commit/bef1e4f637d8f665bc133a9c6d30df08d983bc3a
- http://www.openwall.com/lists/oss-security/2016/09/22/2
- https://github.com/ImageMagick/ImageMagick/issues/120
