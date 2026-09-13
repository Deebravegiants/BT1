# [M] CVE-2018-11254

## Summary
Severity: Medium
Advisory: CVE-2018-11254
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-18
Source: https://osv.dev/vulnerability/CVE-2018-11254
Type: osv

## Details
An issue was discovered in PoDoFo 0.9.5. There is an Excessive Recursion in the PdfPagesTree::GetPageNode() function of PdfPagesTree.cpp. Remote attackers could leverage this vulnerability to cause a denial of service through a crafted pdf file, a related issue to CVE-2017-8054.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1576174
