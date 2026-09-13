# [M] CVE-2016-7522

## Summary
Severity: Medium
Advisory: CVE-2016-7522
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-19
Source: https://osv.dev/vulnerability/CVE-2016-7522
Type: osv

## Details
The ReadPSDImage function in MagickCore/locale.c in ImageMagick allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted PSD file.

## References
- http://www.securityfocus.com/bid/93131
- https://bugs.launchpad.net/ubuntu/+source/imagemagick/+bug/1537419
- https://bugzilla.redhat.com/show_bug.cgi?id=1378751
- http://www.openwall.com/lists/oss-security/2016/09/22/2
- https://github.com/ImageMagick/ImageMagick/commit/4b1b9c0522628887195bad3a6723f7000b0c9a58
- https://github.com/ImageMagick/ImageMagick/issues/93
