# [H] ALPINE-CVE-2018-16844

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-16844
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-16844
Type: osv

## Affected
- Alpine:v3.10: `nginx` — affected >=1.9.5 <1.14.1-r0
- Alpine:v3.11: `nginx` — affected >=1.9.5 <1.14.1-r0
- Alpine:v3.12: `nginx` — affected >=1.9.5 <1.14.1-r0
- Alpine:v3.13: `nginx` — affected >=1.9.5 <1.14.1-r0
- Alpine:v3.14: `nginx` — affected >=1.9.5 <1.14.1-r0
- Alpine:v3.15: `nginx` — affected >=1.9.5 <1.14.1-r0
- Alpine:v3.16: `nginx` — affected >=1.9.5 <1.14.1-r0
- Alpine:v3.17: `nginx` — affected >=1.9.5 <1.14.1-r0
- Alpine:v3.18: `nginx` — affected >=1.9.5 <1.14.1-r0
- Alpine:v3.19: `nginx` — affected >=1.9.5 <1.14.1-r0
- Alpine:v3.20: `nginx` — affected >=1.9.5 <1.14.1-r0
- Alpine:v3.21: `nginx` — affected >=1.9.5 <1.14.1-r0
- Alpine:v3.22: `nginx` — affected >=1.9.5 <1.14.1-r0
- Alpine:v3.23: `nginx` — affected >=1.9.5 <1.14.1-r0
- Alpine:v3.24: `nginx` — affected >=1.9.5 <1.14.1-r0
- Alpine:v3.6: `nginx` — affected >=1.9.5 <1.12.2-r2
- Alpine:v3.7: `nginx` — affected >=1.9.5 <1.12.1-r4
- Alpine:v3.8: `nginx` — affected >=1.9.5 <1.14.1-r0
- Alpine:v3.9: `nginx` — affected >=1.9.5 <1.14.1-r0

## Details
nginx before versions 1.15.6 and 1.14.1 has a vulnerability in the implementation of HTTP/2 that can allow for excessive CPU usage. This issue affects nginx compiled with the ngx_http_v2_module (not compiled by default) if the 'http2' option of the 'listen' directive is used in a configuration file.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-16844
