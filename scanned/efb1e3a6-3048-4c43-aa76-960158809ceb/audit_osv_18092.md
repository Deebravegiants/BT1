# [M] CVE-2020-23914

## Summary
Severity: Medium
Advisory: CVE-2020-23914
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-21
Source: https://osv.dev/vulnerability/CVE-2020-23914
Type: osv

## Details
An issue was discovered in cpp-peglib through v0.1.12. A NULL pointer dereference exists in the peg::AstOptimizer::optimize() located in peglib.h. It allows an attacker to cause Denial of Service.

## References
- https://github.com/yhirose/cpp-peglib/commit/0061f393de54cf0326621c079dc2988336d1ebb3
- https://github.com/yhirose/cpp-peglib/issues/121
