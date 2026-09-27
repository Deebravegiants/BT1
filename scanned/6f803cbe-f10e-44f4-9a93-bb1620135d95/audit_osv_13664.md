# [H] CVE-2018-20751

## Summary
Severity: High
Advisory: CVE-2018-20751
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-04
Source: https://osv.dev/vulnerability/CVE-2018-20751
Type: osv

## Details
An issue was discovered in crop_page in PoDoFo 0.9.6. For a crafted PDF document, pPage->GetObject()->GetDictionary().AddKey(PdfName("MediaBox"),var) can be problematic due to the function GetObject() being called for the pPage NULL pointer object. The value of pPage at this point is 0x0, which causes a NULL pointer dereference.

## References
- https://research.loginsoft.com/bugs/null-pointer-dereference-vulnerability-in-crop_page-podofo-0-9-6/
- https://sourceforge.net/p/podofo/tickets/33/
