# [M] ALPINE-CVE-2019-12781

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-12781
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-07-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12781
Type: osv

## Affected
- Alpine:v3.10: `py-django` — affected >=0 <1.11.22-r0
- Alpine:v3.7: `py-django` — affected >=0 <1.11.22-r0
- Alpine:v3.8: `py-django` — affected >=0 <1.11.22-r0
- Alpine:v3.9: `py-django` — affected >=0 <1.11.22-r0
- Alpine:v3.11: `py3-django` — affected >=0 <1.11.22-r0
- Alpine:v3.12: `py3-django` — affected >=0 <1.11.22-r0

## Details
An issue was discovered in Django 1.11 before 1.11.22, 2.1 before 2.1.10, and 2.2 before 2.2.3. An HTTP request is not redirected to HTTPS when the SECURE_PROXY_SSL_HEADER and SECURE_SSL_REDIRECT settings are used, and the proxy connects to Django via HTTPS. In other words, django.http.HttpRequest.scheme has incorrect behavior when a client uses HTTP.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12781
