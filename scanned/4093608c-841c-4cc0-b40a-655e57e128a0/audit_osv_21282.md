# [H] CVE-2021-41682

## Summary
Severity: High
Advisory: CVE-2021-41682
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-06-20
Source: https://osv.dev/vulnerability/CVE-2021-41682
Type: osv

## Details
There is a heap-use-after-free at ecma-helpers-string.c:1940 in ecma_compare_ecma_non_direct_strings in JerryScript 2.4.0

## References
- https://github.com/jerryscript-project/jerryscript/issues/4747
