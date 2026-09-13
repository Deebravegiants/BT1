# [M] CVE-2016-7514

## Summary
Severity: Medium
Advisory: CVE-2016-7514
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-20
Source: https://osv.dev/vulnerability/CVE-2016-7514
Type: osv

## Details
The ReadPSDChannelPixels function in coders/psd.c in ImageMagick allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted PSD file.

## References
- http://www.securityfocus.com/bid/93122
- https://bugs.launchpad.net/ubuntu/+source/imagemagick/+bug/1533442
- http://www.openwall.com/lists/oss-security/2016/09/22/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1378739
- https://github.com/ImageMagick/ImageMagick/commit/198fffab4daf8aea88badd9c629350e5b26ec32f
- https://github.com/ImageMagick/ImageMagick/commit/280215b9936d145dd5ee91403738ccce1333cab1
- https://github.com/ImageMagick/ImageMagick/commit/6f1879d498bcc5cce12fe0c5decb8dbc0f608e5d
- https://github.com/ImageMagick/ImageMagick/commit/e14fd0a2801f73bdc123baf4fbab97dec55919eb
- https://github.com/ImageMagick/ImageMagick/issues/83
