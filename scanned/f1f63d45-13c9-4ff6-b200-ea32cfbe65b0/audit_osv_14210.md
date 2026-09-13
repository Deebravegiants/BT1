# [H] CVE-2018-8000

## Summary
Severity: High
Advisory: CVE-2018-8000
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-09
Source: https://osv.dev/vulnerability/CVE-2018-8000
Type: osv

## Details
In PoDoFo 0.9.5, there exists a heap-based buffer overflow vulnerability in PoDoFo::PdfTokenizer::GetNextToken() in PdfTokenizer.cpp, a related issue to CVE-2017-5886. Remote attackers could leverage this vulnerability to cause a denial-of-service or potentially execute arbitrary code via a crafted pdf file.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1548918
- https://sourceforge.net/p/podofo/tickets/13/
