# [M] CVE-2021-3508

## Summary
Severity: Medium
Advisory: CVE-2021-3508
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-28
Source: https://osv.dev/vulnerability/CVE-2021-3508
Type: osv

## Details
A flaw was found in PDFResurrect in version 0.22b. There is an infinite loop in get_xref_linear_skipped() in pdf.c via a crafted PDF file.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1951198
- https://github.com/enferex/pdfresurrect/issues/17
