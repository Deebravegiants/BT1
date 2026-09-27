# [H] CVE-2020-23312

## Summary
Severity: High
Advisory: CVE-2020-23312
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-10
Source: https://osv.dev/vulnerability/CVE-2020-23312
Type: osv

## Details
There is an Assertion 'context.status_flags & PARSER_SCANNING_SUCCESSFUL' failed at js-parser.c:2185 in parser_parse_source in JerryScript 2.2.0.

## References
- https://github.com/jerryscript-project/jerryscript/issues/3824
