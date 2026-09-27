# [M] ALPINE-CVE-2023-23936

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-23936
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2023-02-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-23936
Type: osv

## Affected
- Alpine:v3.15: `nodejs` — affected >=0 <16.19.1-r0
- Alpine:v3.16: `nodejs` — affected >=0 <16.19.1-r0
- Alpine:v3.17: `nodejs` — affected >=0 <18.14.1-r0
- Alpine:v3.18: `nodejs` — affected >=0 <18.14.1-r0
- Alpine:v3.19: `nodejs` — affected >=0 <18.14.1-r0
- Alpine:v3.20: `nodejs` — affected >=0 <18.14.1-r0
- Alpine:v3.21: `nodejs` — affected >=0 <18.14.1-r0
- Alpine:v3.22: `nodejs` — affected >=0 <18.14.1-r0
- Alpine:v3.23: `nodejs` — affected >=0 <18.14.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <18.14.1-r0

## Details
Undici is an HTTP/1.1 client for Node.js. Starting with version 2.0.0 and prior to version 5.19.1, the undici library does not protect `host` HTTP header from CRLF injection vulnerabilities. This issue is patched in Undici v5.19.1. As a workaround, sanitize the `headers.host` string before passing to undici.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-23936
