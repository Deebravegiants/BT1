# [M] ALPINE-CVE-2026-27860

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-27860
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-27860
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.3-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.3-r0

## Details
If auth_username_chars is empty, it is possible to inject arbitrary LDAP filter to Dovecot's LDAP authentication. This leads to potentially bypassing restrictions and allows probing of LDAP structure. Do not clear out auth_username_chars, or install fixed version. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-27860
