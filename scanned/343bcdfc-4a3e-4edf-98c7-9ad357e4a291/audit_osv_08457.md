# [M] CVE-2016-3619

## Summary
Severity: Medium
Advisory: CVE-2016-3619
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-10-03
Source: https://osv.dev/vulnerability/CVE-2016-3619
Type: osv

## Details
The DumpModeEncode function in tif_dumpmode.c in the bmp2tiff tool in LibTIFF 4.0.6 and earlier, when the "-c none" option is used, allows remote attackers to cause a denial of service (buffer over-read) via a crafted BMP image.

## References
- http://www.securityfocus.com/bid/85919
- http://www.securitytracker.com/id/1035508
- https://security.gentoo.org/glsa/201701-16
- http://bugzilla.maptools.org/show_bug.cgi?id=2567
- http://www.openwall.com/lists/oss-security/2016/04/07/1
