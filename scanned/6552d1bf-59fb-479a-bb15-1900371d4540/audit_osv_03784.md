# [M] ALPINE-CVE-2026-48928

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-48928
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-48928
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.23.0-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.23.0-r0
- Alpine:v3.23: `nodejs` — affected >=0 <24.17.0-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.17.0-r0

## Details
A inconsistency in Node.js hostname matching can cause a trust-policy bypass in multi-context mTLS setups.

This vulnerability affects all supported release lines: **Node.js 22**, **Node.js 24**, and **Node.js 26**.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-48928
