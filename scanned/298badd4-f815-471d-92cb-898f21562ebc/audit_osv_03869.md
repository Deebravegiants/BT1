# [H] ALPINE-CVE-2026-58043

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-58043
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-58043
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.23.2-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.23.2-r0
- Alpine:v3.23: `nodejs` — affected >=0 <24.18.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.18.1-r0

## Details
A flaw in Node.js Permission Model enforcement can over-grant filesystem access across radix-tree prefix boundaries.

Under `--permission`, an attacker who is granted access to one path can abuse boundary handling to read from or write to paths outside the intended filesystem allowlist.

This vulnerability affects Node.js **main**, **22.x**, **24.x**, and **26.x**.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-58043
