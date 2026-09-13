# [M] CVE-2017-7994

## Summary
Severity: Medium
Advisory: CVE-2017-7994
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-21
Source: https://osv.dev/vulnerability/CVE-2017-7994
Type: osv

## Details
The function TextExtractor::ExtractText in TextExtractor.cpp:77 in PoDoFo 0.9.5 allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted PDF document.

## References
- http://www.securityfocus.com/bid/97980
- https://github.com/icepng/PoC/tree/master/PoC1
- https://icepng.github.io/2017/04/21/PoDoFo-1/
