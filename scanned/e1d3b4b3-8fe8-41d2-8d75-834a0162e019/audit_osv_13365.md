# [H] CVE-2018-19532

## Summary
Severity: High
Advisory: CVE-2018-19532
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-11-26
Source: https://osv.dev/vulnerability/CVE-2018-19532
Type: osv

## Details
A NULL pointer dereference vulnerability exists in the function PdfTranslator::setTarget() in pdftranslator.cpp of PoDoFo 0.9.6, while creating the PdfXObject, as demonstrated by podofoimpose. It allows an attacker to cause Denial of Service.

## References
- https://research.loginsoft.com/bugs/null-pointer-dereference-vulnerability-in-pdftranslatorsettarget-podofo-0-9-6/
- https://sourceforge.net/p/podofo/tickets/32/
