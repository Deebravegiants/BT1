# [M] CVE-2019-9903

## Summary
Severity: Medium
Advisory: CVE-2019-9903
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2019-9903
Type: osv

## Details
PDFDoc::markObject in PDFDoc.cc in Poppler 0.74.0 mishandles dict marking, leading to stack consumption in the function Dict::find() located at Dict.cc, which can (for example) be triggered by passing a crafted pdf file to the pdfunite binary.

## References
- http://www.securityfocus.com/bid/107560
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JQ6RABASMSIMMWMDZTP6ZWUWZPTBSVB5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XGYLZZ4DZUDBQEGCNDWSZPSFNNZJF4S6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XWWVIYFXM74KJFIDHP4W67HR4FRF2LDE/
- https://access.redhat.com/errata/RHSA-2019:2713
- https://lists.debian.org/debian-lts-announce/2022/09/msg00030.html
- https://usn.ubuntu.com/4042-1/
- https://gitlab.freedesktop.org/poppler/poppler/issues/741
- https://research.loginsoft.com/bugs/stack-based-buffer-overflows-in-dictfind-poppler-0-74-0/
