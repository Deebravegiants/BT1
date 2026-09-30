# [M] ALPINE-CVE-2025-9231

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-9231
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2025-09-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-9231
Type: osv

## Affected
- Alpine:v3.20: `openssl` — affected >=0 <3.3.5-r0
- Alpine:v3.21: `openssl` — affected >=0 <3.3.5-r0
- Alpine:v3.22: `openssl` — affected >=0 <3.5.4-r0
- Alpine:v3.23: `openssl` — affected >=0 <3.5.4-r0
- Alpine:v3.24: `openssl` — affected >=0 <3.5.4-r0

## Details
Issue summary: A timing side-channel which could potentially allow remote
recovery of the private key exists in the SM2 algorithm implementation on 64 bit
ARM platforms.

Impact summary: A timing side-channel in SM2 signature computations on 64 bit
ARM platforms could allow recovering the private key by an attacker..

While remote key recovery over a network was not attempted by the reporter,
timing measurements revealed a timing signal which may allow such an attack.

OpenSSL does not directly support certificates with SM2 keys in TLS, and so
this CVE is not relevant in most TLS contexts.  However, given that it is
possible to add support for such certificates via a custom provider, coupled
with the fact that in such a custom provider context the private key may be
recoverable via remote timing measurements, we consider this to be a Moderate
severity issue.

The FIPS modules in 3.5, 3.4, 3.3, 3.2, 3.1 and 3.0 are not affected by this
issue, as SM2 is not an approved algorithm.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-9231
