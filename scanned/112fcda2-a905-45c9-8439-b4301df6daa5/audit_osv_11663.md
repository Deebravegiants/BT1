# [M] CVE-2017-9239

## Summary
Severity: Medium
Advisory: CVE-2017-9239
Aliases: PYSEC-2017-112
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-26
Source: https://osv.dev/vulnerability/CVE-2017-9239
Type: osv

## Details
An issue was discovered in Exiv2 0.26. When the data structure of the structure ifd is incorrect, the program assigns pValue_ to 0x0, and the value of pValue() is 0x0. TiffImageEntry::doWriteImage will use the value of pValue() to cause a segmentation fault. To exploit this vulnerability, someone must open a crafted tiff file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00009.html
- https://github.com/lolo-pop/poc/tree/master/Segmentation%20fault%20in%20convert-test%28exiv2%29
- http://www.securityfocus.com/bid/98720
- https://usn.ubuntu.com/3852-1/
- http://dev.exiv2.org/issues/1295
