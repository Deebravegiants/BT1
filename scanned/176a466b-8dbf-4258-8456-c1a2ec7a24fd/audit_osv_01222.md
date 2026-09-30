# [C] ALPINE-CVE-2018-6758

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-6758
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-6758
Type: osv

## Affected
- Alpine:v3.10: `uwsgi` — affected >=0 <2.0.16-r0
- Alpine:v3.11: `uwsgi` — affected >=0 <2.0.16-r0
- Alpine:v3.12: `uwsgi` — affected >=0 <2.0.16-r0
- Alpine:v3.13: `uwsgi` — affected >=0 <2.0.16-r0
- Alpine:v3.14: `uwsgi` — affected >=0 <2.0.16-r0
- Alpine:v3.15: `uwsgi` — affected >=0 <2.0.16-r0
- Alpine:v3.16: `uwsgi` — affected >=0 <2.0.16-r0
- Alpine:v3.17: `uwsgi` — affected >=0 <2.0.16-r0
- Alpine:v3.18: `uwsgi` — affected >=0 <2.0.16-r0
- Alpine:v3.19: `uwsgi` — affected >=0 <2.0.16-r0
- Alpine:v3.20: `uwsgi` — affected >=0 <2.0.16-r0
- Alpine:v3.21: `uwsgi` — affected >=0 <2.0.16-r0
- Alpine:v3.22: `uwsgi` — affected >=0 <2.0.16-r0
- Alpine:v3.23: `uwsgi` — affected >=0 <2.0.16-r0
- Alpine:v3.24: `uwsgi` — affected >=0 <2.0.16-r0
- Alpine:v3.4: `uwsgi` — affected >=0 <2.0.16-r0
- Alpine:v3.5: `uwsgi` — affected >=0 <2.0.16-r0
- Alpine:v3.6: `uwsgi` — affected >=0 <2.0.16-r0
- Alpine:v3.7: `uwsgi` — affected >=0 <2.0.16-r0
- Alpine:v3.8: `uwsgi` — affected >=0 <2.0.16-r0
- Alpine:v3.9: `uwsgi` — affected >=0 <2.0.16-r0

## Details
The uwsgi_expand_path function in core/utils.c in Unbit uWSGI through 2.0.15 has a stack-based buffer overflow via a large directory length.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-6758
