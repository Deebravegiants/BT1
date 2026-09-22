# [M] ALPINE-CVE-2021-40528

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-40528
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-09-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-40528
Type: osv

## Affected
- Alpine:v3.11: `libgcrypt` — affected >=0 <1.8.8-r1
- Alpine:v3.12: `libgcrypt` — affected >=0 <1.8.8-r1
- Alpine:v3.13: `libgcrypt` — affected >=0 <1.8.8-r1

## Details
The ElGamal implementation in Libgcrypt before 1.9.4 allows plaintext recovery because, during interaction between two cryptographic libraries, a certain dangerous combination of the prime defined by the receiver's public key, the generator defined by the receiver's public key, and the sender's ephemeral exponents can lead to a cross-configuration attack against OpenPGP.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-40528
