# [H] CVE-2017-11335

## Summary
Severity: High
Advisory: CVE-2017-11335
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2017-11335
Type: osv

## Details
There is a heap based buffer overflow in tools/tiff2pdf.c of LibTIFF 4.0.8 via a PlanarConfig=Contig image, which causes a more than one hundred bytes out-of-bounds write (related to the ZIPDecode function in tif_zip.c). A crafted input may lead to a remote denial of service attack or an arbitrary code execution attack.

## References
- https://usn.ubuntu.com/3602-1/
- https://www.debian.org/security/2018/dsa-4100
- http://bugzilla.maptools.org/show_bug.cgi?id=2715
