# [M] ALPINE-CVE-2016-2178

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-2178
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-06-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-2178
Type: osv

## Affected
- Alpine:v3.2: `openssl` — affected >=0 <1.0.2h-r1
- Alpine:v3.3: `openssl` — affected >=0 <1.0.2h-r1
- Alpine:v3.4: `openssl` — affected >=0 <1.0.2h-r1
- Alpine:v3.5: `openssl` — affected >=0 <1.0.2h-r1
- Alpine:v3.6: `openssl` — affected >=0 <1.0.2h-r1
- Alpine:v3.7: `openssl` — affected >=0 <1.0.2h-r1
- Alpine:v3.8: `openssl` — affected >=0 <1.0.2h-r1

## Details
The dsa_sign_setup function in crypto/dsa/dsa_ossl.c in OpenSSL through 1.0.2h does not properly ensure the use of constant-time operations, which makes it easier for local users to discover a DSA private key via a timing side-channel attack.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-2178
