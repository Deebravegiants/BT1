# [M] ALPINE-CVE-2026-40019

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-40019
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-40019
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.5-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.5-r0

## Details
An unauthenticated attacker can send a truncated quoted argument to the ManageSieve login process, which makes it spin in an infinite loop consuming CPU. This can cause degradation or denial of service for Sieve script management, and repeated connections can consume all available CPU on the server. Monitor system for abnormal CPU usage and kill the offending process. Restrict network access to the ManageSieve service to trusted clients. Update to non-vulnerable version. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-40019
