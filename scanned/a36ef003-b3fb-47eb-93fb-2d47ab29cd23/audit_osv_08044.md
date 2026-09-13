# [M] CVE-2016-10095

## Summary
Severity: Medium
Advisory: CVE-2016-10095
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-01
Source: https://osv.dev/vulnerability/CVE-2016-10095
Type: osv

## Details
Stack-based buffer overflow in the _TIFFVGetField function in tif_dir.c in LibTIFF 4.0.0alpha4, 4.0.0alpha5, 4.0.0alpha6, 4.0.0beta7, 4.0.0, 4.0.1, 4.0.2, 4.0.3, 4.0.4, 4.0.4beta, 4.0.5, 4.0.6, 4.0.7 and 4.0.8 allows remote attackers to cause a denial of service (crash) via a crafted TIFF file.

## References
- http://www.securityfocus.com/bid/95178
- http://www.debian.org/security/2017/dsa-3903
- http://www.openwall.com/lists/oss-security/2017/01/01/11
- http://www.openwall.com/lists/oss-security/2017/01/01/7
- http://bugzilla.maptools.org/show_bug.cgi?id=2625
- https://blogs.gentoo.org/ago/2017/01/01/libtiff-stack-based-buffer-overflow-in-_tiffvgetfield-tif_dir-c/
