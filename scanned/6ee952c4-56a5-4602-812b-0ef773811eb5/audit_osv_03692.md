# [M] ALPINE-CVE-2026-42014

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-42014
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42014
Type: osv

## Affected
- Alpine:v3.20: `gnutls` — affected >=0 <3.8.13-r0
- Alpine:v3.21: `gnutls` — affected >=0 <3.8.13-r0
- Alpine:v3.22: `gnutls` — affected >=0 <3.8.13-r0
- Alpine:v3.23: `gnutls` — affected >=0 <3.8.13-r0
- Alpine:v3.24: `gnutls` — affected >=0 <3.8.13-r0

## Details
A flaw was found in GnuTLS. The `gnutls_pkcs11_token_set_pin` function, used for changing the Security Officer PIN, can lead to a use-after-free vulnerability. This occurs when an attacker attempts to change the PIN with a NULL old PIN for a token that lacks a protected authentication path.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42014
