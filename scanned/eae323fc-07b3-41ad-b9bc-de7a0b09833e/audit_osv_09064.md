# [M] CVE-2016-7537

## Summary
Severity: Medium
Advisory: CVE-2016-7537
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-19
Source: https://osv.dev/vulnerability/CVE-2016-7537
Type: osv

## Details
MagickCore/memory.c in ImageMagick allows remote attackers to cause a denial of service (out-of-bounds access) via a crafted PDB file.

## References
- http://www.securityfocus.com/bid/93131
- https://bugs.launchpad.net/ubuntu/+source/imagemagick/+bug/1553366
- http://www.openwall.com/lists/oss-security/2016/09/22/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1378773
- https://github.com/ImageMagick/ImageMagick/commit/424d40ebfcde48bb872eba75179d3d73704fdf1f
- https://github.com/ImageMagick/ImageMagick/commit/6d202a0514fb6a406456b8b728cde776becb25f8
- https://github.com/ImageMagick/ImageMagick/issues/143
