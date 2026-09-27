# [H] ALPINE-CVE-2019-6975

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-6975
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-02-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-6975
Type: osv

## Affected
- Alpine:v3.10: `py-django` — affected >=0 <1.11.19-r0
- Alpine:v3.9: `py-django` — affected >=0 <1.11.19-r0
- Alpine:v3.11: `py3-django` — affected >=0 <1.11.19-r0
- Alpine:v3.12: `py3-django` — affected >=0 <1.11.19-r0

## Details
Django 1.11.x before 1.11.19, 2.0.x before 2.0.11, and 2.1.x before 2.1.6 allows Uncontrolled Memory Consumption via a malicious attacker-supplied value to the django.utils.numberformat.format() function.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-6975
