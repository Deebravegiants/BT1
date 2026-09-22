# [M] CVE-2021-32285

## Summary
Severity: Medium
Advisory: CVE-2021-32285
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/CVE-2021-32285
Type: osv

## Details
An issue was discovered in gravity through 0.8.1. A NULL pointer dereference exists in the function list_iterator_next() located in gravity_core.c. It allows an attacker to cause Denial of Service.

## References
- https://github.com/marcobambini/gravity/issues/319
