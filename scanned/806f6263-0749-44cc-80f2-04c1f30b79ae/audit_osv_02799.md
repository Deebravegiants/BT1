# [H] ALPINE-CVE-2023-27522

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-27522
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-03-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-27522
Type: osv

## Affected
- Alpine:v3.14: `apache2` — affected >=0 <2.4.56-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.56-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.56-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.56-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.56-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.56-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.56-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.56-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.56-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.56-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.56-r0

## Details
HTTP Response Smuggling vulnerability in Apache HTTP Server via mod_proxy_uwsgi. This issue affects Apache HTTP Server: from 2.4.30 through 2.4.55.

Special characters in the origin response header can truncate/split the response forwarded to the client.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-27522
