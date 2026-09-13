# [M] CVE-2021-46340

## Summary
Severity: Medium
Advisory: CVE-2021-46340
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-20
Source: https://osv.dev/vulnerability/CVE-2021-46340
Type: osv

## Details
There is an Assertion 'context_p->stack_top_uint8 == SCAN_STACK_TRY_STATEMENT || context_p->stack_top_uint8 == SCAN_STACK_CATCH_STATEMENT' failed at /parser/js/js-scanner.c(scanner_scan_statement_end) in JerryScript 3.0.0.

## References
- https://github.com/jerryscript-project/jerryscript/issues/4924
