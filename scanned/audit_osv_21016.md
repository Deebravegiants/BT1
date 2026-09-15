# [M] CVE-2021-39532

## Summary
Severity: Medium
Advisory: CVE-2021-39532
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/CVE-2021-39532
Type: osv

## Details
An issue was discovered in libslax through v0.22.1. A NULL pointer dereference exists in the function slaxLexer() located in slaxlexer.c. It allows an attacker to cause Denial of Service.

## References
- https://github.com/Juniper/libslax/issues/50
