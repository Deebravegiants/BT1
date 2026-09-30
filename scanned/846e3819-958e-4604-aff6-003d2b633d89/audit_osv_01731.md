# [M] ALPINE-CVE-2020-12402

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-12402
Ecosystem: Alpine:v3.12, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.4 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2020-07-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-12402
Type: osv

## Affected
- Alpine:v3.12: `nss` — affected >=0 <3.53.1-r0
- Alpine:v3.19: `nss` — affected >=0 <3.53.1-r0
- Alpine:v3.20: `nss` — affected >=0 <3.53.1-r0
- Alpine:v3.21: `nss` — affected >=0 <3.53.1-r0
- Alpine:v3.22: `nss` — affected >=0 <3.53.1-r0
- Alpine:v3.23: `nss` — affected >=0 <3.53.1-r0
- Alpine:v3.24: `nss` — affected >=0 <3.53.1-r0

## Details
During RSA key generation, bignum implementations used a variation of the Binary Extended Euclidean Algorithm which entailed significantly input-dependent flow. This allowed an attacker able to perform electromagnetic-based side channel attacks to record traces leading to the recovery of the secret primes. *Note:* An unmodified Firefox browser does not generate RSA keys in normal operation and is not affected, but products built on top of it might. This vulnerability affects Firefox < 78.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-12402
