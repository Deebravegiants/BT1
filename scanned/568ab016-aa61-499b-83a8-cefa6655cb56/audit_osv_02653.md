# [H] ALPINE-CVE-2022-41859

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-41859
Ecosystem: Alpine:v3.15, Alpine:v3.16
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-01-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-41859
Type: osv

## Affected
- Alpine:v3.15: `freeradius` — affected >=0 <3.0.26-r0
- Alpine:v3.16: `freeradius` — affected >=0 <3.0.26-r0

## Details
In freeradius, the EAP-PWD function compute_password_element() leaks information about the password which allows an attacker to substantially reduce the size of an offline dictionary attack.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-41859
