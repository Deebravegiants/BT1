# [M] CVE-2017-7381

## Summary
Severity: Medium
Advisory: CVE-2017-7381
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-03
Source: https://osv.dev/vulnerability/CVE-2017-7381
Type: osv

## Details
The doc/PdfPage.cpp:609:23 code in PoDoFo 0.9.5 allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted PDF document.

## References
- http://www.securityfocus.com/bid/97296
- https://blogs.gentoo.org/ago/2017/03/31/podofo-four-null-pointer-dereference
