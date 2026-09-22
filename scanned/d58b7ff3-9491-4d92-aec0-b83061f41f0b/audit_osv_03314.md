# [H] ALPINE-CVE-2025-49630

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-49630
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-49630
Type: osv

## Affected
- Alpine:v3.19: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.64-r0

## Details
In certain proxy configurations, a denial of service attack against Apache HTTP Server versions 2.4.26 through to 2.4.63 can be triggered by untrusted clients causing an assertion in mod_proxy_http2.

Configurations affected are a reverse proxy is configured for an HTTP/2 backend, with ProxyPreserveHost set to "on".

## References
- https://security.alpinelinux.org/vuln/CVE-2025-49630
