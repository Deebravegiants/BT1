# [M] CVE-2017-8054

## Summary
Severity: Medium
Advisory: CVE-2017-8054
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-22
Source: https://osv.dev/vulnerability/CVE-2017-8054
Type: osv

## Details
The function PdfPagesTree::GetPageNodeFromArray in PdfPageTree.cpp:464 in PoDoFo 0.9.5 allows remote attackers to cause a denial of service (infinite recursion and application crash) via a crafted PDF document.

## References
- http://qwertwwwe.github.io/2017/04/22/PoDoFo-0-9-5-allows-remote-attackers-to-cause-a-denial-of-service-infinit-loop/
