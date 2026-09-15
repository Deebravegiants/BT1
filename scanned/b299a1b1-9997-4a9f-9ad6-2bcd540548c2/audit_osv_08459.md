# [H] CVE-2016-3621

## Summary
Severity: High
Advisory: CVE-2016-3621
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-10-03
Source: https://osv.dev/vulnerability/CVE-2016-3621
Type: osv

## Details
The LZWEncode function in tif_lzw.c in the bmp2tiff tool in LibTIFF 4.0.6 and earlier, when the "-c lzw" option is used, allows remote attackers to cause a denial of service (buffer over-read) via a crafted BMP image.

## References
- http://www.securitytracker.com/id/1035508
- http://www.openwall.com/lists/oss-security/2016/04/07/3
- https://security.gentoo.org/glsa/201701-16
- http://bugzilla.maptools.org/show_bug.cgi?id=2565
