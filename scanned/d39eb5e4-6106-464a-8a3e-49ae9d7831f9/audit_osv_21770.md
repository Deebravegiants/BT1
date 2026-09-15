# [M] CVE-2021-46346

## Summary
Severity: Medium
Advisory: CVE-2021-46346
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-20
Source: https://osv.dev/vulnerability/CVE-2021-46346
Type: osv

## Details
There is an Assertion 'local_tza == ecma_date_local_time_zone_adjustment (date_value)' failed at /jerry-core/ecma/builtin-objects/ecma-builtin-date-prototype.c(ecma_builtin_date_prototype_dispatch_set):421 in JerryScript 3.0.0.

## References
- https://github.com/jerryscript-project/jerryscript/issues/4939
