# [M] ALPINE-CVE-2018-7536

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-7536
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2018-03-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-7536
Type: osv

## Affected
- Alpine:v3.10: `py-django` — affected >=0 <1.11.11-r0
- Alpine:v3.4: `py-django` — affected >=0 <1.8.19-r0
- Alpine:v3.5: `py-django` — affected >=0 <1.8.19-r0
- Alpine:v3.6: `py-django` — affected >=0 <1.11.11-r0
- Alpine:v3.7: `py-django` — affected >=0 <1.11.11-r0
- Alpine:v3.8: `py-django` — affected >=0 <1.11.11-r0
- Alpine:v3.9: `py-django` — affected >=0 <1.11.11-r0
- Alpine:v3.11: `py3-django` — affected >=0 <1.11.11-r0
- Alpine:v3.12: `py3-django` — affected >=0 <1.11.11-r0

## Details
An issue was discovered in Django 2.0 before 2.0.3, 1.11 before 1.11.11, and 1.8 before 1.8.19. The django.utils.html.urlize() function was extremely slow to evaluate certain inputs due to catastrophic backtracking vulnerabilities in two regular expressions (only one regular expression for Django 1.8.x). The urlize() function is used to implement the urlize and urlizetrunc template filters, which were thus vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-7536
