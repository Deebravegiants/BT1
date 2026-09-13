# [M] CVE-2018-8101

## Summary
Severity: Medium
Advisory: CVE-2018-8101
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-14
Source: https://osv.dev/vulnerability/CVE-2018-8101
Type: osv

## Details
The JPXStream::inverseTransformLevel function in JPXStream.cc in xpdf 4.00 allows attackers to launch denial of service (heap-based buffer over-read and application crash) via a specific pdf file, as demonstrated by pdftohtml.

## References
- https://forum.xpdfreader.com/viewtopic.php?f=3&t=652
