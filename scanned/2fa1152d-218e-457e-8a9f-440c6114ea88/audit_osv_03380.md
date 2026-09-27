# [H] ALPINE-CVE-2025-67733

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-67733
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-02-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-67733
Type: osv

## Affected
- Alpine:v3.21: `valkey` — affected >=8.0.0 <7.2.12-r0
- Alpine:v3.22: `valkey` — affected >=8.0.0 <8.1.6-r0
- Alpine:v3.23: `valkey` — affected >=8.0.0 <9.0.3-r0
- Alpine:v3.24: `valkey` — affected >=8.0.0 <9.0.3-r0

## Details
Valkey is a distributed key-value database. Prior to versions 9.0.2, 8.1.6, 8.0.7, and 7.2.12, a malicious user can use scripting commands to inject arbitrary information into the response stream for the given client, potentially corrupting or returning tampered data to other users on the same connection. The error handling code for lua scripts does not properly handle null characters. Versions 9.0.2, 8.1.6, 8.0.7, and 7.2.12 fix the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-67733
