# [M] ALPINE-CVE-2026-33603

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-33603
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-33603
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.4-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.4-r0

## Details
Attacker can use a specially crafted base64 exchange between Dovecot and Client to fake SCRAM TLS channel binding. This requires that the attacker is able to position itself between Dovecot and the client connection. If successful, the attacker can eavesdrop communications between Dovecot and client as MITM proxy. Install fixed version. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-33603
