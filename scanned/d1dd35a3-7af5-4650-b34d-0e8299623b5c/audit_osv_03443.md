# [H] ALPINE-CVE-2026-13608

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-13608
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-09-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-13608
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=0 <8.22.0-r0

## Details
A flaw in the libcurl SASL negotiation for LDAP authentication allows an
incomplete handshake sequence to be misinterpreted as a successful
cryptographic verification. An attacker executing a Man-in-the-Middle (MITM)
attack can inject a premature or shortcut response that bypasses complete peer
validation.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-13608
