# [M] CVE-2020-24187

## Summary
Severity: Medium
Advisory: CVE-2020-24187
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-08-11
Source: https://osv.dev/vulnerability/CVE-2020-24187
Type: osv

## Details
An issue was discovered in ecma-helpers.c in jerryscript version 2.3.0, allows local attackers to cause a denial of service (DoS) (Null Pointer Dereference).

## References
- https://github.com/jerryscript-project/jerryscript/issues/4076
- https://github.com/Aurorainfinity/Poc/tree/master/jerryscript/NULL-dereference-ecma_get_lex_env_type
