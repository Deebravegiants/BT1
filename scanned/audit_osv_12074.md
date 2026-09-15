# [M] CVE-2018-1002209

## Summary
Severity: Medium
Advisory: CVE-2018-1002209
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2018-07-25
Source: https://osv.dev/vulnerability/CVE-2018-1002209
Type: osv

## Details
QuaZIP before 0.7.6 is vulnerable to directory traversal, allowing attackers to write to arbitrary files via a ../ (dot dot slash) in a Zip archive entry that is mishandled during extraction. This vulnerability is also known as 'Zip-Slip'.

## References
- https://github.com/snyk/zip-slip-vulnerability
- https://github.com/stachenov/quazip/blob/0.7.6/NEWS.txt
- https://snyk.io/research/zip-slip-vulnerability
- https://github.com/stachenov/quazip/commit/5d2fc16a1976e5bf78d2927b012f67a2ae047a98
