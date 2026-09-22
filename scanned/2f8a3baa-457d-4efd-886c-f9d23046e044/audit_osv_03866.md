# [M] ALPINE-CVE-2026-58040

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-58040
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-58040
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.23.2-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.23.2-r0
- Alpine:v3.23: `nodejs` — affected >=0 <24.18.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.18.1-r0

## Details
An incomplete fix has been identified in Node.js: HTTPS Agent TLS session reuse skips hostname verification across identity policies (incomplete fix of CVE-2026-48934).

This vulnerability affects Node.js **22.x**, **24.x**, and **26.x**.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-58040
