# [H] CVE-2017-8787

## Summary
Severity: High
Advisory: CVE-2017-8787
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-05-05
Source: https://osv.dev/vulnerability/CVE-2017-8787
Type: osv

## Details
The PoDoFo::PdfXRefStreamParserObject::ReadXRefStreamEntry function in base/PdfXRefStreamParserObject.cpp:224 in PoDoFo 0.9.5 allows remote attackers to cause a denial of service (heap-based buffer over-read) or possibly have unspecified other impact via a crafted PDF file.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=861738
