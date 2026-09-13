# [H] ALPINE-CVE-2026-48937

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-48937
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-48937
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.23.0-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.23.0-r0
- Alpine:v3.23: `nodejs` — affected >=0 <24.17.0-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.17.0-r0

## Details
A flaw in Node.js HTTP/2 server API can cause servers to keep accepting data even after sending a `GOAWAY` frame. This vulnerability affects two supported release lines: **Node.js 22** and **Node.js 24**.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-48937
