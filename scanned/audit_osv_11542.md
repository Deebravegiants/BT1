# [C] CVE-2017-8378

## Summary
Severity: Critical
Advisory: CVE-2017-8378
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-01
Source: https://osv.dev/vulnerability/CVE-2017-8378
Type: osv

## Details
Heap-based buffer overflow in the PdfParser::ReadObjects function in base/PdfParser.cpp in PoDoFo 0.9.5 allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via vectors related to m_offsets.size.

## References
- https://github.com/xiangxiaobo/poc_and_report/tree/master/podofo_heapoverflow_PdfParser.ReadObjects
