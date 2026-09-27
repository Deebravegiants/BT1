# [M] ALPINE-CVE-2018-0737

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-0737
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-04-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-0737
Type: osv

## Affected
- Alpine:v3.3: `openssl` — affected >=1.0.2b <1.0.2o-r1
- Alpine:v3.4: `openssl` — affected >=1.0.2b <1.0.2o-r2
- Alpine:v3.5: `openssl` — affected >=1.0.2b <1.0.2o-r1
- Alpine:v3.6: `openssl` — affected >=1.0.2b <1.0.2o-r1
- Alpine:v3.7: `openssl` — affected >=1.0.2b <1.0.2o-r1
- Alpine:v3.8: `openssl` — affected >=1.0.2b <1.0.2o-r2

## Details
The OpenSSL RSA Key generation algorithm has been shown to be vulnerable to a cache timing side channel attack. An attacker with sufficient access to mount cache timing attacks during the RSA key generation process could recover the private key. Fixed in OpenSSL 1.1.0i-dev (Affected 1.1.0-1.1.0h). Fixed in OpenSSL 1.0.2p-dev (Affected 1.0.2b-1.0.2o).

## References
- https://security.alpinelinux.org/vuln/CVE-2018-0737
