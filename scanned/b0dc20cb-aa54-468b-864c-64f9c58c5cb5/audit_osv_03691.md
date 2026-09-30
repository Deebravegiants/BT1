# [H] ALPINE-CVE-2026-42013

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-42013
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42013
Type: osv

## Affected
- Alpine:v3.20: `gnutls` — affected >=0 <3.8.13-r0
- Alpine:v3.21: `gnutls` — affected >=0 <3.8.13-r0
- Alpine:v3.22: `gnutls` — affected >=0 <3.8.13-r0
- Alpine:v3.23: `gnutls` — affected >=0 <3.8.13-r0
- Alpine:v3.24: `gnutls` — affected >=0 <3.8.13-r0

## Details
A flaw was found in gnutls. When validating certificates, an oversized Subject Alternative Name (SAN) could cause the validation process to incorrectly fall back to checking the Common Name (CN) field. This could allow a remote attacker to bypass proper certificate validation, potentially leading to spoofing or man-in-the-middle attacks.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42013
