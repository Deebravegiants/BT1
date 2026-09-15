# [H] CVE-2020-23308

## Summary
Severity: High
Advisory: CVE-2020-23308
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-10
Source: https://osv.dev/vulnerability/CVE-2020-23308
Type: osv

## Details
There is an Assertion 'context_p->stack_top_uint8 == LEXER_EXPRESSION_START' at js-parser-expr.c:3565 in parser_parse_expression in JerryScript 2.2.0.

## References
- https://github.com/jerryscript-project/jerryscript/issues/3819
