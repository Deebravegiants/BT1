# [H] CVE-2021-32284

## Summary
Severity: High
Advisory: CVE-2021-32284
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/CVE-2021-32284
Type: osv

## Details
An issue was discovered in gravity through 0.8.1. A NULL pointer dereference exists in the function ircode_register_pop_context_protect() located in gravity_ircode.c. It allows an attacker to cause Denial of Service.

## References
- https://github.com/marcobambini/gravity/issues/321
