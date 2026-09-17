# [M] CVE-2018-20797

## Summary
Severity: Medium
Advisory: CVE-2018-20797
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-27
Source: https://osv.dev/vulnerability/CVE-2018-20797
Type: osv

## Details
An issue was discovered in PoDoFo 0.9.6. There is an attempted excessive memory allocation in PoDoFo::podofo_calloc in base/PdfMemoryManagement.cpp when called from PoDoFo::PdfPredictorDecoder::PdfPredictorDecoder in base/PdfFiltersPrivate.cpp.

## References
- https://sourceforge.net/p/podofo/tickets/34/
