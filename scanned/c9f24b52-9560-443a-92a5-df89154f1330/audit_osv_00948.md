# [M] ALPINE-CVE-2018-12404

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-12404
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-05-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-12404
Type: osv

## Affected
- Alpine:v3.10: `nss` — affected >=0 <3.41-r0
- Alpine:v3.11: `nss` — affected >=0 <3.41-r0
- Alpine:v3.12: `nss` — affected >=0 <3.41-r0
- Alpine:v3.19: `nss` — affected >=0 <3.41-r0
- Alpine:v3.20: `nss` — affected >=0 <3.41-r0
- Alpine:v3.21: `nss` — affected >=0 <3.41-r0
- Alpine:v3.22: `nss` — affected >=0 <3.41-r0
- Alpine:v3.23: `nss` — affected >=0 <3.41-r0
- Alpine:v3.24: `nss` — affected >=0 <3.41-r0
- Alpine:v3.9: `nss` — affected >=0 <3.41-r0

## Details
A cached side channel attack during handshakes using RSA encryption could allow for the decryption of encrypted content. This is a variant of the Adaptive Chosen Ciphertext attack (AKA Bleichenbacher attack) and affects all NSS versions prior to NSS 3.41.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-12404
