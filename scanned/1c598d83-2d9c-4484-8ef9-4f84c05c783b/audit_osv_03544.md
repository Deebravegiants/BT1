# [M] ALPINE-CVE-2026-27855

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-27855
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-27855
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.3-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.3-r0

## Details
Dovecot OTP authentication is vulnerable to replay attack under specific conditions. If auth cache is enabled, and username is altered in passdb, then OTP credentials can be cached so that same OTP reply is valid. An attacker able to observe an OTP exchange is able to log in as the user. If authentication happens over unsecure connection, switch to SCRAM protocol. Alternatively ensure the communcations are secured, and if possible switch to OAUTH2 or SCRAM. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-27855
