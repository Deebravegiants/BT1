# [M] ALPINE-CVE-2019-1547

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-1547
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-09-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-1547
Type: osv

## Affected
- Alpine:v3.10: `openssl` — affected >=1.0.2 <1.1.1d-r0
- Alpine:v3.11: `openssl` — affected >=1.0.2 <1.1.1d-r1
- Alpine:v3.12: `openssl` — affected >=1.0.2 <1.1.1d-r1
- Alpine:v3.13: `openssl` — affected >=1.0.2 <1.1.1d-r1
- Alpine:v3.14: `openssl` — affected >=1.0.2 <1.1.1d-r1
- Alpine:v3.15: `openssl` — affected >=1.0.2 <1.1.1d-r1
- Alpine:v3.16: `openssl` — affected >=1.0.2 <1.1.1d-r1
- Alpine:v3.17: `openssl` — affected >=1.0.2 <1.1.1d-r1
- Alpine:v3.18: `openssl` — affected >=1.0.2 <1.1.1d-r1
- Alpine:v3.19: `openssl` — affected >=1.0.2 <1.1.1d-r1
- Alpine:v3.20: `openssl` — affected >=1.0.2 <1.1.1d-r1
- Alpine:v3.21: `openssl` — affected >=1.0.2 <1.1.1d-r1
- Alpine:v3.22: `openssl` — affected >=1.0.2 <1.1.1d-r1
- Alpine:v3.23: `openssl` — affected >=1.0.2 <1.1.1d-r1
- Alpine:v3.24: `openssl` — affected >=1.0.2 <1.1.1d-r1
- Alpine:v3.7: `openssl` — affected >=1.0.2 <1.0.2t-r0
- Alpine:v3.8: `openssl` — affected >=1.0.2 <1.0.2t-r0
- Alpine:v3.9: `openssl` — affected >=1.0.2 <1.1.1d-r0
- Alpine:v3.15: `openssl3` — affected >=0 <1.1.1d-r1
- Alpine:v3.16: `openssl3` — affected >=0 <1.1.1d-r1

## Details
Normally in OpenSSL EC groups always have a co-factor present and this is used in side channel resistant code paths. However, in some cases, it is possible to construct a group using explicit parameters (instead of using a named curve). In those cases it is possible that such a group does not have the cofactor present. This can occur even where all the parameters match a known named curve. If such a curve is used then OpenSSL falls back to non-side channel resistant code paths which may result in full key recovery during an ECDSA signature operation. In order to be vulnerable an attacker would have to have the ability to time the creation of a large number of signatures where explicit parameters with no co-factor present are in use by an application using libcrypto. For the avoidance of doubt libssl is not vulnerable because explicit parameters are never used. Fixed in OpenSSL 1.1.1d (Affected 1.1.1-1.1.1c). Fixed in OpenSSL 1.1.0l (Affected 1.1.0-1.1.0k). Fixed in OpenSSL 1.0.2t (Affected 1.0.2-1.0.2s).

## References
- https://security.alpinelinux.org/vuln/CVE-2019-1547
