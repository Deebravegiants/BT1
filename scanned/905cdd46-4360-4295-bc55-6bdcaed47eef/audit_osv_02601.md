# [C] ALPINE-CVE-2022-35255

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-35255
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-12-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-35255
Type: osv

## Affected
- Alpine:v3.15: `nodejs` — affected >=0 <16.17.1-r0
- Alpine:v3.16: `nodejs` — affected >=0 <16.17.1-r0
- Alpine:v3.17: `nodejs` — affected >=0 <16.17.1-r0
- Alpine:v3.18: `nodejs` — affected >=0 <16.17.1-r0
- Alpine:v3.19: `nodejs` — affected >=0 <16.17.1-r0
- Alpine:v3.20: `nodejs` — affected >=0 <16.17.1-r0
- Alpine:v3.21: `nodejs` — affected >=0 <16.17.1-r0
- Alpine:v3.22: `nodejs` — affected >=0 <16.17.1-r0
- Alpine:v3.23: `nodejs` — affected >=0 <16.17.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <16.17.1-r0

## Details
A weak randomness in WebCrypto keygen vulnerability exists in Node.js 18 due to a change with EntropySource() in SecretKeyGenTraits::DoKeyGen() in src/crypto/crypto_keygen.cc. There are two problems with this: 1) It does not check the return value, it assumes EntropySource() always succeeds, but it can (and sometimes will) fail. 2) The random data returned byEntropySource() may not be cryptographically strong and therefore not suitable as keying material.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-35255
