# [H] CVE-2017-2814

## Summary
Severity: High
Advisory: CVE-2017-2814
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-12
Source: https://osv.dev/vulnerability/CVE-2017-2814
Type: osv

## Details
An exploitable heap overflow vulnerability exists in the image rendering functionality of Poppler 0.53.0. A specifically crafted pdf can cause an image resizing after allocation has already occurred, resulting in heap corruption which can lead to code execution. An attacker controlled PDF file can be used to trigger this vulnerability.

## References
- http://www.securityfocus.com/bid/99497
- https://talosintelligence.com/vulnerability_reports/TALOS-2017-0311
