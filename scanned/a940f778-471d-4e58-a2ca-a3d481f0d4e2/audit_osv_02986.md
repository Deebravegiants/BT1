# [M] ALPINE-CVE-2024-13176

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-13176
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.1 (CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-01-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-13176
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=0 <3.0.19-r0
- Alpine:v3.18: `openssl` — affected >=0 <3.1.8-r0
- Alpine:v3.19: `openssl` — affected >=0 <3.1.8-r0
- Alpine:v3.20: `openssl` — affected >=0 <3.3.2-r2
- Alpine:v3.21: `openssl` — affected >=0 <3.3.2-r5
- Alpine:v3.22: `openssl` — affected >=0 <3.3.2-r5
- Alpine:v3.23: `openssl` — affected >=0 <3.3.2-r5
- Alpine:v3.24: `openssl` — affected >=0 <3.3.2-r5

## Details
Issue summary: A timing side-channel which could potentially allow recovering
the private key exists in the ECDSA signature computation.

Impact summary: A timing side-channel in ECDSA signature computations
could allow recovering the private key by an attacker. However, measuring
the timing would require either local access to the signing application or
a very fast network connection with low latency.

There is a timing signal of around 300 nanoseconds when the top word of
the inverted ECDSA nonce value is zero. This can happen with significant
probability only for some of the supported elliptic curves. In particular
the NIST P-521 curve is affected. To be able to measure this leak, the attacker
process must either be located in the same physical computer or must
have a very fast network connection with low latency. For that reason
the severity of this vulnerability is Low.

The FIPS modules in 3.4, 3.3, 3.2, 3.1 and 3.0 are affected by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-13176
