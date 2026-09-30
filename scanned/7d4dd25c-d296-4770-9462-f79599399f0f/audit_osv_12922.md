# [H] CVE-2018-16375

## Summary
Severity: High
Advisory: CVE-2018-16375
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-03
Source: https://osv.dev/vulnerability/CVE-2018-16375
Type: osv

## Details
An issue was discovered in OpenJPEG 2.3.0. Missing checks for header_info.height and header_info.width in the function pnmtoimage in bin/jpwl/convert.c can lead to a heap-based buffer overflow.

## References
- http://www.securityfocus.com/bid/105266
- https://github.com/uclouvain/openjpeg/issues/1126
