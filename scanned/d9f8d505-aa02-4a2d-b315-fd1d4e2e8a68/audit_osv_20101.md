# [M] CVE-2021-30470

## Summary
Severity: Medium
Advisory: CVE-2021-30470
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2021-30470
Type: osv

## Details
A flaw was found in PoDoFo 0.9.7. An uncontrolled recursive call among PdfTokenizer::ReadArray(), PdfTokenizer::GetNextVariant() and PdfTokenizer::ReadDataType() functions can lead to a stack overflow.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1947436
