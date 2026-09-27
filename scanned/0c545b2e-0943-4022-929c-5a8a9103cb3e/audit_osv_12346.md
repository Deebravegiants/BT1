# [C] CVE-2018-11419

## Summary
Severity: Critical
Advisory: CVE-2018-11419
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-24
Source: https://osv.dev/vulnerability/CVE-2018-11419
Type: osv

## Details
An issue was discovered in JerryScript 1.0. There is a heap-based buffer over-read in the lit_read_code_unit_from_hex function via a RegExp("[\\u0") payload, related to re_parse_char_class in parser/regexp/re-parser.c.

## References
- https://github.com/jerryscript-project/jerryscript/issues/2230
