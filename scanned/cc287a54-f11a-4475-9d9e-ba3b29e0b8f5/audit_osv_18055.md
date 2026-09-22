# [H] CVE-2020-23319

## Summary
Severity: High
Advisory: CVE-2020-23319
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-10
Source: https://osv.dev/vulnerability/CVE-2020-23319
Type: osv

## Details
There is an Assertion in '(flags >> CBC_STACK_ADJUST_SHIFT) >= CBC_STACK_ADJUST_BASE || (CBC_STACK_ADJUST_BASE - (flags >> CBC_STACK_ADJUST_SHIFT)) <= context_p->stack_depth' in parser_emit_cbc_backward_branch in JerryScript 2.2.0.

## References
- https://github.com/jerryscript-project/jerryscript/issues/3834
