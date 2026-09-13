# [C] CVE-2018-13008

## Summary
Severity: Critical
Advisory: CVE-2018-13008
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-29
Source: https://osv.dev/vulnerability/CVE-2018-13008
Type: osv

## Details
An issue was discovered in gpmf-parser 1.1.2. There is a heap-based buffer over-read in GPMF_parser.c in the function GPMF_Next, related to certain checks for a positive nest_level.

## References
- https://github.com/gopro/gpmf-parser/issues/29
