# [M] ALPINE-CVE-2026-40020

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-40020
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-40020
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.4-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.4-r0

## Details
Attacker can use the IMAP SETACL command to inject the anyone permission to user's dovecot-acl file even if imap_acl_allow_anyone=no. This causes folders to be spammed to all users. The impact is limited to being able to spam folders to other users, no unexpected access is gained. Install to fixed version. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-40020
