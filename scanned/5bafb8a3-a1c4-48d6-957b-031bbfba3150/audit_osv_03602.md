# [M] ALPINE-CVE-2026-33606

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-33606
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-33606
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.5-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.5-r0

## Details
Mail content stored by a user can be crafted so that it is interpreted as dsync protocol commands when an administrator later runs dsync with the stream protocol, for example during a migration. Injected commands can modify mailbox state on the destination during migration or replication, including internal mailbox attributes that a user should not be able to set directly. It can also cause dsync errors. Avoid running dsync with the stream protocol on mailboxes with untrusted content. Update to non-vulnerable version. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-33606
