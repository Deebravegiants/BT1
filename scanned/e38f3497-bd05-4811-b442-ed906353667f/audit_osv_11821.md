# [M] CVE-2017-9937

## Summary
Severity: Medium
Advisory: CVE-2017-9937
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-26
Source: https://osv.dev/vulnerability/CVE-2017-9937
Type: osv

## Details
In LibTIFF 4.0.8, there is a memory malloc failure in tif_jbig.c. A crafted TIFF document can lead to an abort resulting in a remote denial of service attack.

## References
- https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772%40%3Cdev.mina.apache.org%3E
- http://www.securityfocus.com/bid/99304
- http://bugzilla.maptools.org/show_bug.cgi?id=2707
