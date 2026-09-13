# [H] CVE-2019-20087

## Summary
Severity: High
Advisory: CVE-2019-20087
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-12-30
Source: https://osv.dev/vulnerability/CVE-2019-20087
Type: osv

## Details
GoPro GPMF-parser 1.2.3 has a heap-based buffer over-read in GPMF_seekToSamples in GPMF-parse.c for the "matching tags" feature.

## References
- https://github.com/gopro/gpmf-parser/issues/76
