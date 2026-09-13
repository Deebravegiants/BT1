# [M] CVE-2017-9815

## Summary
Severity: Medium
Advisory: CVE-2017-9815
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-22
Source: https://osv.dev/vulnerability/CVE-2017-9815
Type: osv

## Details
In LibTIFF 4.0.7, the TIFFReadDirEntryLong8Array function in libtiff/tif_dirread.c mishandles a malloc operation, which allows attackers to cause a denial of service (memory leak within the function _TIFFmalloc in tif_unix.c) via a crafted file.

## References
- http://somevulnsofadlab.blogspot.jp/2017/06/libtiffmemory-leak-in-tiffmalloc.html
- http://www.securityfocus.com/bid/99235
- https://usn.ubuntu.com/3602-1/
- http://bugzilla.maptools.org/show_bug.cgi?id=2682
