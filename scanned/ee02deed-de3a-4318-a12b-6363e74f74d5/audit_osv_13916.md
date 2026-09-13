# [M] CVE-2018-5296

## Summary
Severity: Medium
Advisory: CVE-2018-5296
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-08
Source: https://osv.dev/vulnerability/CVE-2018-5296
Type: osv

## Details
In PoDoFo 0.9.5, there is an uncontrolled memory allocation in the PdfParser::ReadXRefSubsection function (base/PdfParser.cpp). Remote attackers could leverage this vulnerability to cause a denial-of-service via a crafted pdf file.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1531956
