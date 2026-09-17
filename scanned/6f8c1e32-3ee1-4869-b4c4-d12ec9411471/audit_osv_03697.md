# [M] ALPINE-CVE-2026-42392

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-42392
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42392
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.5-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.5-r0

## Details
An attacker that has valid credentials can send an invalid IMAP URLFETCH command, which causes uninitialized memory to be included in the error response returned to the client. Process memory contents can be disclosed to the client, which may include sensitive data. Disable the IMAP URLAUTH functionality. Update to non-vulnerable version. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42392
