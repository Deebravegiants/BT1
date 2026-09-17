# [M] CVE-2017-5855

## Summary
Severity: Medium
Advisory: CVE-2017-5855
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-01
Source: https://osv.dev/vulnerability/CVE-2017-5855
Type: osv

## Details
The PoDoFo::PdfParser::ReadXRefSubsection function in PdfParser.cpp in PoDoFo 0.9.4 allows remote attackers to cause a denial of service (NULL pointer dereference) via a crafted file.

## References
- http://www.securityfocus.com/bid/96516
- https://blogs.gentoo.org/ago/2017/02/01/podofo-null-pointer-dereference-in-podofopdfparserreadxrefsubsection-pdfparser-cpp/
