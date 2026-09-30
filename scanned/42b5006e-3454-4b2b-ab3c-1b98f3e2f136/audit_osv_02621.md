# [M] ALPINE-CVE-2022-37436

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-37436
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-01-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-37436
Type: osv

## Affected
- Alpine:v3.14: `apache2` — affected >=0 <2.4.55-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.55-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.55-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.55-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.55-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.55-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.55-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.55-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.55-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.55-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.55-r0

## Details
Prior to Apache HTTP Server 2.4.55, a malicious backend can cause the response headers to be truncated early, resulting in some headers being incorporated into the response body. If the later headers have any security purpose, they will not be interpreted by the client.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-37436
