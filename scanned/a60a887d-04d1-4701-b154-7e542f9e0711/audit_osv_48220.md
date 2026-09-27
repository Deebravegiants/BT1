# [H] CVE-2017-2820

## Summary
Severity: High
Advisory: CVE-2017-2820
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-12
Source: https://osv.dev/vulnerability/CVE-2017-2820
Type: osv

## Details
An exploitable integer overflow vulnerability exists in the JPEG 2000 image parsing functionality of freedesktop.org Poppler 0.53.0. A specially crafted PDF file can lead to an integer overflow causing out of bounds memory overwrite on the heap resulting in potential arbitrary code execution. To trigger this vulnerability, a victim must open the malicious PDF in an application using this library.

## References
- http://www.securityfocus.com/bid/99497
- https://talosintelligence.com/vulnerability_reports/TALOS-2017-0321
