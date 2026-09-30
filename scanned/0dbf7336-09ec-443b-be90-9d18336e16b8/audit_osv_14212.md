# [H] CVE-2018-8002

## Summary
Severity: High
Advisory: CVE-2018-8002
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-09
Source: https://osv.dev/vulnerability/CVE-2018-8002
Type: osv

## Details
In PoDoFo 0.9.5, there exists an infinite loop vulnerability in PdfParserObject::ParseFileComplete() in PdfParserObject.cpp which may result in stack overflow. Remote attackers could leverage this vulnerability to cause a denial-of-service or possibly unspecified other impact via a crafted pdf file.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1548930
- https://www.exploit-db.com/exploits/44946/
