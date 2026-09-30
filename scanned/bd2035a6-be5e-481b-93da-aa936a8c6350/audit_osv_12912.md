# [H] CVE-2018-16335

## Summary
Severity: High
Advisory: CVE-2018-16335
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-02
Source: https://osv.dev/vulnerability/CVE-2018-16335
Type: osv

## Details
newoffsets handling in ChopUpSingleUncompressedStrip in tif_dirread.c in LibTIFF 4.0.9 allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted TIFF file, as demonstrated by tiff2pdf. This is a different vulnerability than CVE-2018-15209.

## References
- https://www.debian.org/security/2018/dsa-4349
- http://bugzilla.maptools.org/show_bug.cgi?id=2809
