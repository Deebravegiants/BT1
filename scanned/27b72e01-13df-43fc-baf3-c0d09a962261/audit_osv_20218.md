# [H] CVE-2021-32281

## Summary
Severity: High
Advisory: CVE-2021-32281
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/CVE-2021-32281
Type: osv

## Details
An issue was discovered in gravity through 0.8.1. A heap-buffer-overflow exists in the function gnode_function_add_upvalue located in gravity_ast.c. It allows an attacker to cause code Execution.

## References
- https://github.com/marcobambini/gravity/issues/313
