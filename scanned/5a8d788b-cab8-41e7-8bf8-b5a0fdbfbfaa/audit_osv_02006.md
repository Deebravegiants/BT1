# [C] ALPINE-CVE-2020-7471

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2020-7471
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-7471
Type: osv

## Affected
- Alpine:v3.10: `py-django` — affected >=0 <1.11.28-r0
- Alpine:v3.8: `py-django` — affected >=0 <1.11.28-r0
- Alpine:v3.9: `py-django` — affected >=0 <1.11.28-r0
- Alpine:v3.11: `py3-django` — affected >=0 <1.11.28-r0
- Alpine:v3.12: `py3-django` — affected >=0 <1.11.28-r0

## Details
Django 1.11 before 1.11.28, 2.2 before 2.2.10, and 3.0 before 3.0.3 allows SQL Injection if untrusted data is used as a StringAgg delimiter (e.g., in Django applications that offer downloads of data as a series of rows with a user-specified column delimiter). By passing a suitably crafted delimiter to a contrib.postgres.aggregates.StringAgg instance, it was possible to break escaping and inject malicious SQL.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-7471
