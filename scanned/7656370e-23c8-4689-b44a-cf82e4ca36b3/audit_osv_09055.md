# [M] CVE-2016-7528

## Summary
Severity: Medium
Advisory: CVE-2016-7528
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-19
Source: https://osv.dev/vulnerability/CVE-2016-7528
Type: osv

## Details
The ReadVIFFImage function in coders/viff.c in ImageMagick allows remote attackers to cause a denial of service (segmentation fault) via a crafted VIFF file.

## References
- http://www.securityfocus.com/bid/93226
- https://bugs.launchpad.net/ubuntu/+source/imagemagick/+bug/1537425
- https://bugzilla.redhat.com/show_bug.cgi?id=1378760
- http://www.openwall.com/lists/oss-security/2016/09/22/2
- https://github.com/ImageMagick/ImageMagick/commit/7be16a280014f895a951db4948df316a23dabc09
- https://github.com/ImageMagick/ImageMagick/commit/ca0c886abd6d3ef335eb74150cd23b89ebd17135
- https://github.com/ImageMagick/ImageMagick/issues/99
