# [H] ALPINE-CVE-2018-7490

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-7490
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-02-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-7490
Type: osv

## Affected
- Alpine:v3.4: `uwsgi` — affected >=0 <2.0.17-r0
- Alpine:v3.5: `uwsgi` — affected >=0 <2.0.17-r0
- Alpine:v3.6: `uwsgi` — affected >=0 <2.0.17-r0
- Alpine:v3.7: `uwsgi` — affected >=0 <2.0.17-r0

## Details
uWSGI before 2.0.17 mishandles a DOCUMENT_ROOT check during use of the --php-docroot option, allowing directory traversal.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-7490
