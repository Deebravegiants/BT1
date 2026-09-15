# [H] CVE-2018-5308

## Summary
Severity: High
Advisory: CVE-2018-5308
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-01-09
Source: https://osv.dev/vulnerability/CVE-2018-5308
Type: osv

## Details
PoDoFo 0.9.5 does not properly validate memcpy arguments in the PdfMemoryOutputStream::Write function (base/PdfOutputStream.cpp). Remote attackers could leverage this vulnerability to cause a denial-of-service or possibly unspecified other impact via a crafted pdf file.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1532390
