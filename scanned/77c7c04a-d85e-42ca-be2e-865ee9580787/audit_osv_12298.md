# [M] CVE-2018-11255

## Summary
Severity: Medium
Advisory: CVE-2018-11255
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-18
Source: https://osv.dev/vulnerability/CVE-2018-11255
Type: osv

## Details
An issue was discovered in PoDoFo 0.9.5. The function PdfPage::GetPageNumber() in PdfPage.cpp in PoDoFo 0.9.5 allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted PDF document.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1575502
