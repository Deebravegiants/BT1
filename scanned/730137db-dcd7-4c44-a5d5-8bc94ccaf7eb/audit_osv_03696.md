# [H] ALPINE-CVE-2026-42391

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-42391
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42391
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.5-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.5-r0

## Details
An unauthenticated attacker can send an IMAP ID command with a very large number of parameters before logging in, which causes memory and CPU usage to grow disproportionately. The login process can be terminated by the out-of-memory handling, which also terminates all other connections handled by the same process. This can cause degradation or denial of service for IMAP logins. Limit the number of connections handled by a single imap-login process. This has a performance impact though. Update to non-vulnerable version. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42391
