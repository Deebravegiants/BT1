# [H] CVE-2019-20089

## Summary
Severity: High
Advisory: CVE-2019-20089
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-12-30
Source: https://osv.dev/vulnerability/CVE-2019-20089
Type: osv

## Details
GoPro GPMF-parser 1.2.3 has an heap-based buffer over-read in GPMF_SeekToSamples in GPMF_parse.c for the size calculation.

## References
- https://github.com/gopro/gpmf-parser/issues/75
