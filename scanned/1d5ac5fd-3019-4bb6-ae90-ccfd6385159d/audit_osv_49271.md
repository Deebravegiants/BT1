# [H] CVE-2018-8100

## Summary
Severity: High
Advisory: CVE-2018-8100
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-14
Source: https://osv.dev/vulnerability/CVE-2018-8100
Type: osv

## Details
The JPXStream::readTilePart function in JPXStream.cc in xpdf 4.00 allows attackers to launch denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a specific pdf file, as demonstrated by pdftohtml.

## References
- https://forum.xpdfreader.com/viewtopic.php?f=3&t=652
