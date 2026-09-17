# [M] CVE-2018-7453

## Summary
Severity: Medium
Advisory: CVE-2018-7453
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-24
Source: https://osv.dev/vulnerability/CVE-2018-7453
Type: osv

## Details
Infinite recursion in AcroForm::scanField in AcroForm.cc in xpdf 4.00 allows attackers to launch denial of service via a specific pdf file due to lack of loop checking, as demonstrated by pdftohtml.

## References
- https://forum.xpdfreader.com/viewtopic.php?p=814#p814
