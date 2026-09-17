# [M] ALPINE-CVE-2026-33607

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-33607
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-33607
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.5-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.5-r0

## Details
An attacker that has valid credentials can use IMAP LIST command to consume CPU. This can cause degradation or denial of service for IMAP. Monitor system for abnormal CPU usage and kill the offending process and lock account. Alternatively install fixed version. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-33607
