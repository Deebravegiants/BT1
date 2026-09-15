# [C] ALPINE-CVE-2026-27851

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-27851
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-27851
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.4-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.4-r0

## Details
When safe filter is used with variable expansion, all following pipelines on the same string are incorrectly interpreted as safe too, enabling unsafe data to be unescaped. This can enable SQL / LDAP injection attacks when used in authentication. Avoid using safe filter until on fixed version. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-27851
