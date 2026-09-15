# [M] ALPINE-CVE-2019-1551

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-1551
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-12-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-1551
Type: osv

## Affected
- Alpine:v3.10: `openssl` — affected >=1.0.2 <1.1.1d-r2
- Alpine:v3.11: `openssl` — affected >=1.0.2 <1.1.1d-r3
- Alpine:v3.12: `openssl` — affected >=1.0.2 <1.1.1d-r3
- Alpine:v3.13: `openssl` — affected >=1.0.2 <1.1.1d-r3
- Alpine:v3.14: `openssl` — affected >=1.0.2 <1.1.1d-r3
- Alpine:v3.15: `openssl` — affected >=1.0.2 <1.1.1d-r3
- Alpine:v3.16: `openssl` — affected >=1.0.2 <1.1.1d-r3
- Alpine:v3.17: `openssl` — affected >=1.0.2 <1.1.1d-r3
- Alpine:v3.18: `openssl` — affected >=1.0.2 <1.1.1d-r3
- Alpine:v3.19: `openssl` — affected >=1.0.2 <1.1.1d-r3
- Alpine:v3.20: `openssl` — affected >=1.0.2 <1.1.1d-r3
- Alpine:v3.21: `openssl` — affected >=1.0.2 <1.1.1d-r3
- Alpine:v3.22: `openssl` — affected >=1.0.2 <1.1.1d-r3
- Alpine:v3.23: `openssl` — affected >=1.0.2 <1.1.1d-r3
- Alpine:v3.24: `openssl` — affected >=1.0.2 <1.1.1d-r3
- Alpine:v3.8: `openssl` — affected >=1.0.2 <1.0.2u-r0
- Alpine:v3.9: `openssl` — affected >=1.0.2 <1.1.1d-r2
- Alpine:v3.15: `openssl3` — affected >=0 <1.1.1d-r3
- Alpine:v3.16: `openssl3` — affected >=0 <1.1.1d-r3

## Details
There is an overflow bug in the x64_64 Montgomery squaring procedure used in exponentiation with 512-bit moduli. No EC algorithms are affected. Analysis suggests that attacks against 2-prime RSA1024, 3-prime RSA1536, and DSA1024 as a result of this defect would be very difficult to perform and are not believed likely. Attacks against DH512 are considered just feasible. However, for an attack the target would have to re-use the DH512 private key, which is not recommended anyway. Also applications directly using the low level API BN_mod_exp may be affected if they use BN_FLG_CONSTTIME. Fixed in OpenSSL 1.1.1e (Affected 1.1.1-1.1.1d). Fixed in OpenSSL 1.0.2u (Affected 1.0.2-1.0.2t).

## References
- https://security.alpinelinux.org/vuln/CVE-2019-1551
