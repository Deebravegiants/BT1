# [M] CVE-2018-16369

## Summary
Severity: Medium
Advisory: CVE-2018-16369
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-03
Source: https://osv.dev/vulnerability/CVE-2018-16369
Type: osv

## Details
XRef::fetch in XRef.cc in Xpdf 4.00 allows remote attackers to cause a denial of service (stack consumption) via a crafted pdf file, related to AcroForm::scanField, as demonstrated by pdftohtml. NOTE: this might overlap CVE-2018-7453.

## References
- https://github.com/TeamSeri0us/pocs/tree/master/xpdf
