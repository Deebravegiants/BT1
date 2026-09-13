# [H] ALPINE-CVE-2025-59028

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-59028
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-59028
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.3-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.3-r0

## Details
When sending invalid base64 SASL data, login process is disconnected from the auth server, causing all active authentication sessions to fail. Invalid BASE64 data can be used to DoS a vulnerable server to break concurrent logins. Install fixed version or disable concurrency in login processes (heavy perfomance penalty on large deployments). No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-59028
