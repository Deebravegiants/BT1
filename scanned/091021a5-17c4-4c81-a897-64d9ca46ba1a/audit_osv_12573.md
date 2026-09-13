# [C] CVE-2018-13007

## Summary
Severity: Critical
Advisory: CVE-2018-13007
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-29
Source: https://osv.dev/vulnerability/CVE-2018-13007
Type: osv

## Details
An issue was discovered in gpmf-parser 1.1.2. There is a heap-based buffer over-read in GPMF_parser.c in the function GPMF_Next, related to certain checks for GPMF_KEY_END and nest_level (not conditional on a buffer_size_longs check).

## References
- https://github.com/gopro/gpmf-parser/issues/29
