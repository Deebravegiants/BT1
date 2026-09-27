# [H] CVE-2016-3620

## Summary
Severity: High
Advisory: CVE-2016-3620
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-10-03
Source: https://osv.dev/vulnerability/CVE-2016-3620
Type: osv

## Details
The ZIPEncode function in tif_zip.c in the bmp2tiff tool in LibTIFF 4.0.6 and earlier, when the "-c zip" option is used, allows remote attackers to cause a denial of service (buffer over-read) via a crafted BMP image.

## References
- http://www.securitytracker.com/id/1035508
- https://security.gentoo.org/glsa/201701-16
- http://bugzilla.maptools.org/show_bug.cgi?id=2570
- http://www.openwall.com/lists/oss-security/2016/04/07/2
