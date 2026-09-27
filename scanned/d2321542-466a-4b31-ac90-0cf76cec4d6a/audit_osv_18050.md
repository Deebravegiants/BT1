# [H] CVE-2020-23310

## Summary
Severity: High
Advisory: CVE-2020-23310
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-10
Source: https://osv.dev/vulnerability/CVE-2020-23310
Type: osv

## Details
There is an Assertion 'context_p->next_scanner_info_p->type == SCANNER_TYPE_FUNCTION' failed at js-parser-statm.c:733 in parser_parse_function_statement in JerryScript 2.2.0.

## References
- https://github.com/jerryscript-project/jerryscript/issues/3821
