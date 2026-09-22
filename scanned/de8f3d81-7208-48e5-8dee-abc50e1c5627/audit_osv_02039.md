# [H] ALPINE-CVE-2020-9402

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-9402
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-9402
Type: osv

## Affected
- Alpine:v3.10: `py-django` — affected >=0 <1.11.29-r0
- Alpine:v3.8: `py-django` — affected >=0 <1.11.29-r0
- Alpine:v3.9: `py-django` — affected >=0 <1.11.29-r0
- Alpine:v3.11: `py3-django` — affected >=0 <1.11.29-r0
- Alpine:v3.12: `py3-django` — affected >=0 <1.11.29-r0

## Details
Django 1.11 before 1.11.29, 2.2 before 2.2.11, and 3.0 before 3.0.4 allows SQL Injection if untrusted data is used as a tolerance parameter in GIS functions and aggregates on Oracle. By passing a suitably crafted tolerance to GIS functions and aggregates on Oracle, it was possible to break escaping and inject malicious SQL.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-9402
