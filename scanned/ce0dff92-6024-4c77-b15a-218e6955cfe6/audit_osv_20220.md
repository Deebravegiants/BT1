# [M] CVE-2021-32283

## Summary
Severity: Medium
Advisory: CVE-2021-32283
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/CVE-2021-32283
Type: osv

## Details
An issue was discovered in gravity through 0.8.1. A NULL pointer dereference exists in the function gravity_string_to_value() located in gravity_value.c. It allows an attacker to cause Denial of Service.

## References
- https://github.com/marcobambini/gravity/issues/314
