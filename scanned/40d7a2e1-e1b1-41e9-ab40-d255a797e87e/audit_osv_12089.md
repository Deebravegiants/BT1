# [M] CVE-2018-10126

## Summary
Severity: Medium
Advisory: CVE-2018-10126
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-04-21
Source: https://osv.dev/vulnerability/CVE-2018-10126
Type: osv

## Details
ijg-libjpeg before 9d, as used in tiff2pdf (from LibTIFF) and other products, does not check for a NULL pointer at a certain place in jpeg_fdct_16x16 in jfdctint.c.

## References
- https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772%40%3Cdev.mina.apache.org%3E
- http://bugzilla.maptools.org/show_bug.cgi?id=2786
- https://gitlab.com/libtiff/libtiff/-/issues/128
