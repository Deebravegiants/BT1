# [H] CVE-2020-23311

## Summary
Severity: High
Advisory: CVE-2020-23311
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-10
Source: https://osv.dev/vulnerability/CVE-2020-23311
Type: osv

## Details
There is an Assertion 'context_p->token.type == LEXER_RIGHT_BRACE || context_p->token.type == LEXER_ASSIGN || context_p->token.type == LEXER_COMMA' failed at js-parser-expr.c:3230 in parser_parse_object_initializer in JerryScript 2.2.0.

## References
- https://github.com/jerryscript-project/jerryscript/issues/3822
