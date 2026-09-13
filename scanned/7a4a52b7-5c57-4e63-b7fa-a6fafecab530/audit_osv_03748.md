# [C] ALPINE-CVE-2026-4480

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-4480
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-4480
Type: osv

## Affected
- Alpine:v3.23: `samba` — affected >=4.1.0 <4.22.10-r0
- Alpine:v3.24: `samba` — affected >=4.1.0 <4.23.8-r0

## Details
A flaw was found in the Samba printing subsystem. Samba passes the client-controlled job description string to the command configured with the "print command" setting via the "%J"
substitution character without escaping shell meta characters. A remote attacker could exploit this vulnerability by sending a specially crafted print job description that contains unescaped shell characters. This could lead to remote code execution on the affected system.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-4480
