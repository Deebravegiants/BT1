# [C] CVE-2018-13421

## Summary
Severity: Critical
Advisory: CVE-2018-13421
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-07
Source: https://osv.dev/vulnerability/CVE-2018-13421
Type: osv

## Details
Fast C++ CSV Parser (aka fast-cpp-csv-parser) before 2018-07-06 has a heap-based buffer over-read in io::trim_chars in csv.h.

## References
- https://github.com/ben-strasser/fast-cpp-csv-parser/issues/67
