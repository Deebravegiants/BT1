# [H] CVE-2017-2818

## Summary
Severity: High
Advisory: CVE-2017-2818
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-12
Source: https://osv.dev/vulnerability/CVE-2017-2818
Type: osv

## Details
An exploitable heap overflow vulnerability exists in the image rendering functionality of Poppler 0.53.0. A specifically crafted PDF can cause an overly large number of color components during image rendering, resulting in heap corruption. An attacker controlled PDF file can be used to trigger this vulnerability.

## References
- http://www.securityfocus.com/bid/99497
- https://talosintelligence.com/vulnerability_reports/TALOS-2017-0319
