# [H] CVE-2018-8001

## Summary
Severity: High
Advisory: CVE-2018-8001
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-09
Source: https://osv.dev/vulnerability/CVE-2018-8001
Type: osv

## Details
In PoDoFo 0.9.5, there exists a heap-based buffer over-read vulnerability in UnescapeName() in PdfName.cpp. Remote attackers could leverage this vulnerability to cause a denial-of-service or possibly unspecified other impact via a crafted pdf file.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1549469
