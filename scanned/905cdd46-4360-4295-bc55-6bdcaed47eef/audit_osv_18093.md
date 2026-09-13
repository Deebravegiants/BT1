# [M] CVE-2020-23915

## Summary
Severity: Medium
Advisory: CVE-2020-23915
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-21
Source: https://osv.dev/vulnerability/CVE-2020-23915
Type: osv

## Details
An issue was discovered in cpp-peglib through v0.1.12. peg::resolve_escape_sequence() in peglib.h has a heap-based buffer over-read.

## References
- https://github.com/yhirose/cpp-peglib/issues/122
- https://github.com/yhirose/cpp-peglib/commit/b3b29ce8f3acf3a32733d930105a17d7b0ba347e
- https://cwe.mitre.org/data/definitions/126.html
