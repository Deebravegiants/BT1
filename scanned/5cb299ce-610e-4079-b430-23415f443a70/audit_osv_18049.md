# [H] CVE-2020-23309

## Summary
Severity: High
Advisory: CVE-2020-23309
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-10
Source: https://osv.dev/vulnerability/CVE-2020-23309
Type: osv

## Details
There is an Assertion 'context_p->stack_depth == context_p->context_stack_depth' failed at js-parser-statm.c:2756 in parser_parse_statements in JerryScript 2.2.0.

## References
- https://github.com/jerryscript-project/jerryscript/issues/3820
