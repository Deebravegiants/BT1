# [C] ALPINE-CVE-2016-9013

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-9013
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-9013
Type: osv

## Affected
- Alpine:v3.10: `py-django` — affected >=0 <1.8.16-r0
- Alpine:v3.2: `py-django` — affected >=0 <1.8.16-r0
- Alpine:v3.3: `py-django` — affected >=0 <1.8.16-r0
- Alpine:v3.4: `py-django` — affected >=0 <1.8.16-r0
- Alpine:v3.5: `py-django` — affected >=0 <1.8.16-r0
- Alpine:v3.6: `py-django` — affected >=0 <1.8.16-r0
- Alpine:v3.7: `py-django` — affected >=0 <1.8.16-r0
- Alpine:v3.8: `py-django` — affected >=0 <1.8.16-r0
- Alpine:v3.9: `py-django` — affected >=0 <1.8.16-r0
- Alpine:v3.11: `py3-django` — affected >=0 <1.8.16-r0
- Alpine:v3.12: `py3-django` — affected >=0 <1.8.16-r0

## Details
Django 1.8.x before 1.8.16, 1.9.x before 1.9.11, and 1.10.x before 1.10.3 use a hardcoded password for a temporary database user created when running tests with an Oracle database, which makes it easier for remote attackers to obtain access to the database server by leveraging failure to manually specify a password in the database settings TEST dictionary.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-9013
