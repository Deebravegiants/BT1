# [M] CVE-2021-46342

## Summary
Severity: Medium
Advisory: CVE-2021-46342
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-20
Source: https://osv.dev/vulnerability/CVE-2021-46342
Type: osv

## Details
There is an Assertion 'ecma_is_lexical_environment (obj_p) || !ecma_op_object_is_fast_array (obj_p)' failed at /jerry-core/ecma/base/ecma-helpers.c in JerryScript 3.0.0.

## References
- https://github.com/jerryscript-project/jerryscript/issues/4934
