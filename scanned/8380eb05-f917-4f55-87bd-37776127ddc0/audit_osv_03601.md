# [H] ALPINE-CVE-2026-33605

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-33605
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-33605
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.5-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.5-r0

## Details
An unauthenticated attacker can crash the ManageSieve login process by sending a small malformed command before authenticating. If running in high-security mode (default for community releases), only the attacker's own connection is terminated. If running in high-performance mode (default for Pro releases), all connections handled by the same managesieve-login process are terminated. Repeating the attack can cause denial of service for Sieve script management. Restrict network access to the ManageSieve service to trusted clients. Update to non-vulnerable version. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-33605
