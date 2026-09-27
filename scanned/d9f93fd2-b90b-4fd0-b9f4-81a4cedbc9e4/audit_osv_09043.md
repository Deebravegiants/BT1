# [M] CVE-2016-7516

## Summary
Severity: Medium
Advisory: CVE-2016-7516
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-20
Source: https://osv.dev/vulnerability/CVE-2016-7516
Type: osv

## Details
The ReadVIFFImage function in coders/viff.c in ImageMagick allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted VIFF file.

## References
- http://www.securityfocus.com/bid/93129
- https://bugs.launchpad.net/ubuntu/+source/imagemagick/+bug/1533452
- http://www.openwall.com/lists/oss-security/2016/09/22/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1378743
- https://github.com/ImageMagick/ImageMagick/issues/77
