# [M] ALPINE-CVE-2026-40016

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-40016
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-40016
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.4-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.4-r0

## Details
Attacker can upload a malicious Sieve script over ManageSieve service (or locally) to bypass configured CPU time limits for Sieve up to 130 times of the configured limit. Attacker can use this to degrade server performance and bypass configured CPU time limits for Sieve scripts. Install fixed version, or alternatively prevent direct access to Sieve scripts via ManageSieve or local access. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-40016
