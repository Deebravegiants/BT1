# [M] ALPINE-CVE-2026-48618

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-48618
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-48618
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.23.0-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.23.0-r0
- Alpine:v3.23: `nodejs` — affected >=0 <24.17.0-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.17.0-r0

## Details
A flaw in Node.js TLS hostname handling can cause Node.js unicode dot separator handling can lead to tls wildcard-depth authentication bypass due to resolver and verifier hostname normalization mismat.

This can lead to confidentiality impact or bypass of the intended security boundary under affected configurations.

This vulnerability affects all supported release lines: **Node.js 22**, **Node.js 24**, and **Node.js 26**.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-48618
