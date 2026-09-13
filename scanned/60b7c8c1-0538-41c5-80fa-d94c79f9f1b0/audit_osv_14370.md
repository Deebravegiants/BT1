# [H] CVE-2018-9918

## Summary
Severity: High
Advisory: CVE-2018-9918
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-10
Source: https://osv.dev/vulnerability/CVE-2018-9918
Type: osv

## Details
libqpdf.a in QPDF through 8.0.2 mishandles certain "expected dictionary key but found non-name object" cases, allowing remote attackers to cause a denial of service (stack exhaustion), related to the QPDFObjectHandle and QPDF_Dictionary classes, because nesting in direct objects is not restricted.

## References
- https://usn.ubuntu.com/3638-1/
- https://github.com/qpdf/qpdf/commit/b4d6cf6836ce025ba1811b7bbec52680c7204223
- https://github.com/qpdf/qpdf/issues/202
