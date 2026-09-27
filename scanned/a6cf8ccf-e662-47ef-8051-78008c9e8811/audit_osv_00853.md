# [H] ALPINE-CVE-2018-0732

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-0732
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-0732
Type: osv

## Affected
- Alpine:v3.10: `libressl` — affected >=0 <2.7.4-r0
- Alpine:v3.11: `libressl` — affected >=0 <2.7.4-r0
- Alpine:v3.12: `libressl` — affected >=0 <2.7.4-r0
- Alpine:v3.13: `libressl` — affected >=0 <2.7.4-r0
- Alpine:v3.7: `libressl` — affected >=0 <2.6.5-r0
- Alpine:v3.8: `libressl` — affected >=0 <2.7.4-r0
- Alpine:v3.9: `libressl` — affected >=0 <2.7.4-r0
- Alpine:v3.3: `openssl` — affected >=1.0.2 <1.0.2o-r1
- Alpine:v3.4: `openssl` — affected >=1.0.2 <1.0.2o-r1
- Alpine:v3.5: `openssl` — affected >=1.0.2 <1.0.2o-r1
- Alpine:v3.6: `openssl` — affected >=1.0.2 <1.0.2o-r1
- Alpine:v3.7: `openssl` — affected >=1.0.2 <1.0.2o-r1
- Alpine:v3.8: `openssl` — affected >=1.0.2 <1.0.2o-r1

## Details
During key agreement in a TLS handshake using a DH(E) based ciphersuite a malicious server can send a very large prime value to the client. This will cause the client to spend an unreasonably long period of time generating a key for this prime resulting in a hang until the client has finished. This could be exploited in a Denial Of Service attack. Fixed in OpenSSL 1.1.0i-dev (Affected 1.1.0-1.1.0h). Fixed in OpenSSL 1.0.2p-dev (Affected 1.0.2-1.0.2o).

## References
- https://security.alpinelinux.org/vuln/CVE-2018-0732
