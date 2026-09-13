# [M] CVE-2019-10723

## Summary
Severity: Medium
Advisory: CVE-2019-10723
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-04-03
Source: https://osv.dev/vulnerability/CVE-2019-10723
Type: osv

## Details
An issue was discovered in PoDoFo 0.9.6. The PdfPagesTreeCache class in doc/PdfPagesTreeCache.cpp has an attempted excessive memory allocation because nInitialSize is not validated.

## References
- https://sourceforge.net/p/podofo/tickets/46/
