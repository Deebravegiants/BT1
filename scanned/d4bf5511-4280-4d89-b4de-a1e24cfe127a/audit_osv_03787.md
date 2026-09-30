# [H] ALPINE-CVE-2026-48933

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-48933
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-48933
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.23.0-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.23.0-r0
- Alpine:v3.23: `nodejs` — affected >=0 <24.17.0-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.17.0-r0

## Details
A flaw in Node.js WebCrypto implementation can crash the process if the input of `subtle.encrypt()` is a multiple of 2GiB.

This vulnerability affects all supported release lines: **Node.js 22**, **Node.js 24**, and **Node.js 26**.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-48933
