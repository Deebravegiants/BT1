# [M] ALPINE-CVE-2024-28835

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-28835
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-03-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-28835
Type: osv

## Affected
- Alpine:v3.18: `gnutls` — affected >=0 <3.8.4-r0
- Alpine:v3.19: `gnutls` — affected >=0 <3.8.4-r0
- Alpine:v3.20: `gnutls` — affected >=0 <3.8.5-r0
- Alpine:v3.21: `gnutls` — affected >=0 <3.8.5-r0
- Alpine:v3.22: `gnutls` — affected >=0 <3.8.5-r0
- Alpine:v3.23: `gnutls` — affected >=0 <3.8.5-r0
- Alpine:v3.24: `gnutls` — affected >=0 <3.8.5-r0

## Details
A flaw has been discovered in GnuTLS where an application crash can be induced when attempting to verify a specially crafted .pem bundle using the "certtool --verify-chain" command.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-28835
