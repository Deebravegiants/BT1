# [H] ALPINE-CVE-2023-0361

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-0361
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-02-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-0361
Type: osv

## Affected
- Alpine:v3.14: `gnutls` — affected >=0 <3.7.1-r2
- Alpine:v3.15: `gnutls` — affected >=0 <3.7.1-r2
- Alpine:v3.16: `gnutls` — affected >=0 <3.7.7-r1
- Alpine:v3.17: `gnutls` — affected >=0 <3.7.8-r3
- Alpine:v3.18: `gnutls` — affected >=0 <3.8.0-r0
- Alpine:v3.19: `gnutls` — affected >=0 <3.8.0-r0
- Alpine:v3.20: `gnutls` — affected >=0 <3.8.0-r0
- Alpine:v3.21: `gnutls` — affected >=0 <3.8.0-r0
- Alpine:v3.22: `gnutls` — affected >=0 <3.8.0-r0
- Alpine:v3.23: `gnutls` — affected >=0 <3.8.0-r0
- Alpine:v3.24: `gnutls` — affected >=0 <3.8.0-r0

## Details
A timing side-channel in the handling of RSA ClientKeyExchange messages was discovered in GnuTLS. This side-channel can be sufficient to recover the key encrypted in the RSA ciphertext across a network in a Bleichenbacher style attack. To achieve a successful decryption the attacker would need to send a large amount of specially crafted messages to the vulnerable server. By recovering the secret from the ClientKeyExchange message, the attacker would be able to decrypt the application data exchanged over that connection.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-0361
