# [M] CVE-2017-5854

## Summary
Severity: Medium
Advisory: CVE-2017-5854
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-01
Source: https://osv.dev/vulnerability/CVE-2017-5854
Type: osv

## Details
base/PdfOutputStream.cpp in PoDoFo 0.9.4 allows remote attackers to cause a denial of service (NULL pointer dereference and crash) via a crafted file.

## References
- http://www.securityfocus.com/bid/96072
- http://www.openwall.com/lists/oss-security/2017/02/01/14
- http://www.openwall.com/lists/oss-security/2017/02/02/12
- https://blogs.gentoo.org/ago/2017/02/01/podofo-null-pointer-dereference-in-pdfoutputstream-cpp/
