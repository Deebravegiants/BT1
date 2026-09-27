# [M] CVE-2016-7532

## Summary
Severity: Medium
Advisory: CVE-2016-7532
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-20
Source: https://osv.dev/vulnerability/CVE-2016-7532
Type: osv

## Details
coders/psd.c in ImageMagick allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted PSD file.

## References
- http://www.securityfocus.com/bid/93131
- https://bugs.launchpad.net/ubuntu/+source/imagemagick/+bug/1539066
- http://www.openwall.com/lists/oss-security/2016/09/22/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1378764
- https://github.com/ImageMagick/ImageMagick/commit/4f2c04ea6673863b87ac7f186cbb0d911f74085c
- https://github.com/ImageMagick/ImageMagick/issues/109
