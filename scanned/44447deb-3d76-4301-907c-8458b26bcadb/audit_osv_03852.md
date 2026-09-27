# [H] ALPINE-CVE-2026-56846

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-56846
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-56846
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.23.2-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.23.2-r0
- Alpine:v3.23: `nodejs` — affected >=0 <24.18.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.18.1-r0

## Details
A flaw in Node.js HTTP/2 handling can cause HTTP/2 retained header blocks evade maxSessionMemory and enable remote memory exhaustion.

This vulnerability affects Node.js **24.x** and **22.x**.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-56846
