# [H] CVE-2017-9250

## Summary
Severity: High
Advisory: CVE-2017-9250
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-28
Source: https://osv.dev/vulnerability/CVE-2017-9250
Type: osv

## Details
The lexer_process_char_literal function in jerry-core/parser/js/js-lexer.c in JerryScript 1.0 does not skip memory allocation for empty strings, which allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via malformed JavaScript source code, related to the jmem_heap_free_block function.

## References
- http://www.securitytracker.com/id/1038413
- https://github.com/zherczeg/jerryscript/commit/03a8c630f015f63268639d3ed3bf82cff6fa77d8
- https://github.com/jerryscript-project/jerryscript/commit/e58f2880df608652aff7fd35c45b242467ec0e79
- https://github.com/jerryscript-project/jerryscript/issues/1821
