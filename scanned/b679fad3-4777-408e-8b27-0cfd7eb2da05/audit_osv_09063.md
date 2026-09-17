# [M] CVE-2016-7536

## Summary
Severity: Medium
Advisory: CVE-2016-7536
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-20
Source: https://osv.dev/vulnerability/CVE-2016-7536
Type: osv

## Details
magick/profile.c in ImageMagick allows remote attackers to cause a denial of service (segmentation fault) via a crafted profile.

## References
- http://www.securityfocus.com/bid/93225
- https://bugs.launchpad.net/ubuntu/+source/imagemagick/+bug/1545367
- https://bugzilla.redhat.com/show_bug.cgi?id=1378772
- http://www.openwall.com/lists/oss-security/2016/09/22/2
- https://github.com/ImageMagick/ImageMagick/commit/02dadf116124cfba35d7ebd9ced3e5ad0be0f176
- https://github.com/ImageMagick/ImageMagick/commit/478cce544fdf1de882d78381768458f397964453
- https://github.com/ImageMagick/ImageMagick/issues/130
