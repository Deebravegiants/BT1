# [M] ALPINE-CVE-2026-56850

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-56850
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-56850
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.23.2-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.23.2-r0
- Alpine:v3.23: `nodejs` — affected >=0 <24.18.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.18.1-r0

## Details
A flaw in Node.js HTTPS Agent connection reuse can cause PFX object-array key collisions, allowing mutual TLS (mTLS) client identities to be reused across requests configured with different client certificates.

This vulnerability affects Node.js **26.x**, **24.x**, and **22.x**.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-56850
