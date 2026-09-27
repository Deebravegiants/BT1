# [M] ALPINE-CVE-2018-1283

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-1283
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-03-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1283
Type: osv

## Affected
- Alpine:v3.10: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.11: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.12: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.13: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.4: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.5: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.6: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.7: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.8: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.9: `apache2` — affected >=0 <2.4.33-r0

## Details
In Apache httpd 2.4.0 to 2.4.29, when mod_session is configured to forward its session data to CGI applications (SessionEnv on, not the default), a remote user may influence their content by using a "Session" header. This comes from the "HTTP_SESSION" variable name used by mod_session to forward its data to CGIs, since the prefix "HTTP_" is also used by the Apache HTTP Server to pass HTTP header fields, per CGI specifications.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1283
