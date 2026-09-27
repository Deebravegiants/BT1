# [H] CVE-2017-12944

## Summary
Severity: High
Advisory: CVE-2017-12944
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-18
Source: https://osv.dev/vulnerability/CVE-2017-12944
Type: osv

## Details
The TIFFReadDirEntryArray function in tif_read.c in LibTIFF 4.0.8 mishandles memory allocation for short files, which allows remote attackers to cause a denial of service (allocation failure and application crash) in the TIFFFetchStripThing function in tif_dirread.c during a tiff2pdf invocation.

## References
- https://usn.ubuntu.com/3602-1/
- https://usn.ubuntu.com/3606-1/
- https://www.debian.org/security/2018/dsa-4100
- http://bugzilla.maptools.org/show_bug.cgi?id=2725
