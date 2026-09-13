# [M] CVE-2019-20093

## Summary
Severity: Medium
Advisory: CVE-2019-20093
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-12-30
Source: https://osv.dev/vulnerability/CVE-2019-20093
Type: osv

## Details
The PoDoFo::PdfVariant::DelayedLoad function in PdfVariant.h in PoDoFo 0.9.6 allows remote attackers to cause a denial of service (NULL pointer dereference) via a crafted file, because of ImageExtractor.cpp.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CTB2J5XWOEGAJYR2N66GAECUIKDG6O2S/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XHFOCBZCF3GX7A6FWE3JM7P37TQWGINJ/
- https://sourceforge.net/p/podofo/tickets/75/
