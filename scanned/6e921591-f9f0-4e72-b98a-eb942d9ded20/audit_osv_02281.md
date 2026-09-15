# [C] ALPINE-CVE-2021-39275

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-39275
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-39275
Type: osv

## Affected
- Alpine:v3.11: `apache2` — affected >=0 <2.4.49-r0
- Alpine:v3.12: `apache2` — affected >=0 <2.4.49-r0
- Alpine:v3.13: `apache2` — affected >=0 <2.4.49-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.49-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.49-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.49-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.49-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.49-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.49-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.49-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.49-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.49-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.49-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.49-r0

## Details
ap_escape_quotes() may write beyond the end of a buffer when given malicious input. No included modules pass untrusted data to these functions, but third-party / external modules may. This issue affects Apache HTTP Server 2.4.48 and earlier.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-39275
