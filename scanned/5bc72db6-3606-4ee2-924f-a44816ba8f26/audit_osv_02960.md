# [H] ALPINE-CVE-2024-0553

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-0553
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-01-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-0553
Type: osv

## Affected
- Alpine:v3.18: `gnutls` — affected >=0 <3.8.3-r0
- Alpine:v3.19: `gnutls` — affected >=0 <3.8.3-r0
- Alpine:v3.20: `gnutls` — affected >=0 <3.8.3-r0
- Alpine:v3.21: `gnutls` — affected >=0 <3.8.3-r0
- Alpine:v3.22: `gnutls` — affected >=0 <3.8.3-r0
- Alpine:v3.23: `gnutls` — affected >=0 <3.8.3-r0
- Alpine:v3.24: `gnutls` — affected >=0 <3.8.3-r0

## Details
A vulnerability was found in GnuTLS. The response times to malformed ciphertexts in RSA-PSK ClientKeyExchange differ from the response times of ciphertexts with correct PKCS#1 v1.5 padding. This issue may allow a remote attacker to perform a timing side-channel attack in the RSA-PSK key exchange, potentially leading to the leakage of sensitive data. CVE-2024-0553 is designated as an incomplete resolution for CVE-2023-5981.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-0553
