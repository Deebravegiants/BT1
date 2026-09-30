# [M] ALPINE-CVE-2026-58045

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-58045
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.2 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-58045
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.23.2-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.23.2-r0
- Alpine:v3.23: `nodejs` — affected >=0 <24.18.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.18.1-r0

## Details
A flaw in Node.js allows a spoofed `TypedArray` `byteLength` to trigger a reachable assertion in the synchronous `node:zlib` APIs, causing the entire process to crash. All 11 synchronous zlib functions are affected.

Repeated exploitation of this condition can result in a denial of service.

This vulnerability affects Node.js **22.x**, **24.x**, and **26.x**.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-58045
