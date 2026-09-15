# [M] CVE-2016-5240

## Summary
Severity: Medium
Advisory: CVE-2016-5240
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-27
Source: https://osv.dev/vulnerability/CVE-2016-5240
Type: osv

## Details
The DrawDashPolygon function in magick/render.c in GraphicsMagick before 1.3.24 and the SVG renderer in ImageMagick allow remote attackers to cause a denial of service (infinite loop) by converting a circularly defined SVG file.

## References
- http://hg.graphicsmagick.org/hg/GraphicsMagick?cmd=changeset%3Bnode=ddc999ec896c
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.securityfocus.com/bid/89348
- https://access.redhat.com/errata/RHSA-2016:1237
- http://www.openwall.com/lists/oss-security/2016/05/01/6
- http://www.openwall.com/lists/oss-security/2016/06/02/14
- http://www.debian.org/security/2016/dsa-3746
- http://www.graphicsmagick.org/ChangeLog-2016.html
- http://www.openwall.com/lists/oss-security/2016/05/01/4
