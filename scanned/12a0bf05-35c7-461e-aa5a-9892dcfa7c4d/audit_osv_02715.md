# [M] ALPINE-CVE-2022-43552

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-43552
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-43552
Type: osv

## Affected
- Alpine:v3.14: `curl` — affected >=0 <7.79.1-r4
- Alpine:v3.15: `curl` — affected >=0 <7.80.0-r5
- Alpine:v3.16: `curl` — affected >=0 <7.83.1-r5
- Alpine:v3.17: `curl` — affected >=0 <7.87.0-r0
- Alpine:v3.18: `curl` — affected >=0 <7.87.0-r0
- Alpine:v3.19: `curl` — affected >=0 <7.87.0-r0
- Alpine:v3.20: `curl` — affected >=0 <7.87.0-r0
- Alpine:v3.21: `curl` — affected >=0 <7.87.0-r0
- Alpine:v3.22: `curl` — affected >=0 <7.87.0-r0
- Alpine:v3.23: `curl` — affected >=0 <7.87.0-r0
- Alpine:v3.24: `curl` — affected >=0 <7.87.0-r0

## Details
A use after free vulnerability exists in curl <7.87.0. Curl can be asked to *tunnel* virtually all protocols it supports through an HTTP proxy. HTTP proxies can (and often do) deny such tunnel operations. When getting denied to tunnel the specific protocols SMB or TELNET, curl would use a heap-allocated struct after it had been freed, in its transfer shutdown code path.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-43552
