# [H] CVE-2015-8870

## Summary
Severity: High
Advisory: CVE-2015-8870
CVSS: 7.4 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2016-12-06
Source: https://osv.dev/vulnerability/CVE-2015-8870
Type: osv

## Details
Integer overflow in tools/bmp2tiff.c in LibTIFF before 4.0.4 allows remote attackers to cause a denial of service (heap-based buffer over-read), or possibly obtain sensitive information from process memory, via crafted width and length values in RLE4 or RLE8 data in a BMP file.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0225.html
- http://www.floyd.ch/?p=874BMP
- http://download.osgeo.org/libtiff/tiff-4.0.4.tar.gz
- http://www.securityfocus.com/bid/94717
