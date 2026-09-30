# [M] ALPINE-CVE-2026-40015

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-40015
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-40015
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.5-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.5-r0

## Details
An attacker that has valid credentials can open many connections to the imap-hibernate service and send invalid commands, which can intermittently cause an out-of-bounds read and crash the process. The crash interrupts hibernated IMAP sessions handled by the affected process, which can cause degradation of service for IMAP. Disable IMAP hibernation. Update to non-vulnerable version. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-40015
