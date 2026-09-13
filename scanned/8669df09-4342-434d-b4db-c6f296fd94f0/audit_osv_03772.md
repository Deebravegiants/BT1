# [H] ALPINE-CVE-2026-48615

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-48615
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-48615
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.23.0-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.23.0-r0
- Alpine:v3.23: `nodejs` — affected >=0 <24.17.0-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.17.0-r0

## Details
A flaw in Node.js proxy tunnel error handling could expose proxy credentials in `ERR_PROXY_TUNNEL` error messages.

When proxy credentials are embedded in the proxy URL, they may be exposed through error handling paths and captured by logs, diagnostics, or other error consumers.

This vulnerability affects all supported release lines: **Node.js 22**, **Node.js 24**, and **Node.js 26**.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-48615
