# [H] CVE-2020-27778

## Summary
Severity: High
Advisory: CVE-2020-27778
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-03
Source: https://osv.dev/vulnerability/CVE-2020-27778
Type: osv

## Details
A flaw was found in Poppler in the way certain PDF files were converted into HTML. A remote attacker could exploit this flaw by providing a malicious PDF file that, when processed by the 'pdftohtml' program, would crash the application causing a denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2022/09/msg00030.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1900712
