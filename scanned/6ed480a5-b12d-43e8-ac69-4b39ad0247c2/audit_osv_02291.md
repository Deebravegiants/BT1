# [M] ALPINE-CVE-2021-40529

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-40529
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-09-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-40529
Type: osv

## Affected
- Alpine:v3.14: `botan` — affected >=0 <2.17.3-r3
- Alpine:v3.15: `botan` — affected >=0 <2.18.1-r3
- Alpine:v3.16: `botan` — affected >=0 <2.18.1-r3
- Alpine:v3.17: `botan` — affected >=0 <2.18.1-r3
- Alpine:v3.18: `botan` — affected >=0 <2.18.1-r3
- Alpine:v3.19: `botan` — affected >=0 <2.18.1-r3
- Alpine:v3.20: `botan` — affected >=0 <2.18.1-r3
- Alpine:v3.21: `botan` — affected >=0 <2.18.1-r3

## Details
The ElGamal implementation in Botan through 2.18.1, as used in Thunderbird and other products, allows plaintext recovery because, during interaction between two cryptographic libraries, a certain dangerous combination of the prime defined by the receiver's public key, the generator defined by the receiver's public key, and the sender's ephemeral exponents can lead to a cross-configuration attack against OpenPGP.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-40529
