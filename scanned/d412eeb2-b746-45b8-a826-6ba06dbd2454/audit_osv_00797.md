# [H] ALPINE-CVE-2017-9022

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-9022
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9022
Type: osv

## Affected
- Alpine:v3.10: `strongswan` — affected >=0 <5.5.3-r0
- Alpine:v3.11: `strongswan` — affected >=0 <5.5.3-r0
- Alpine:v3.12: `strongswan` — affected >=0 <5.5.3-r0
- Alpine:v3.13: `strongswan` — affected >=0 <5.5.3-r0
- Alpine:v3.14: `strongswan` — affected >=0 <5.5.3-r0
- Alpine:v3.15: `strongswan` — affected >=0 <5.5.3-r0
- Alpine:v3.16: `strongswan` — affected >=0 <5.5.3-r0
- Alpine:v3.17: `strongswan` — affected >=0 <5.5.3-r0
- Alpine:v3.18: `strongswan` — affected >=0 <5.5.3-r0
- Alpine:v3.19: `strongswan` — affected >=0 <5.5.3-r0
- Alpine:v3.2: `strongswan` — affected >=0 <5.3.5-r2
- Alpine:v3.20: `strongswan` — affected >=0 <5.5.3-r0
- Alpine:v3.21: `strongswan` — affected >=0 <5.5.3-r0
- Alpine:v3.22: `strongswan` — affected >=0 <5.5.3-r0
- Alpine:v3.23: `strongswan` — affected >=0 <5.5.3-r0
- Alpine:v3.24: `strongswan` — affected >=0 <5.5.3-r0
- Alpine:v3.3: `strongswan` — affected >=0 <5.3.5-r2
- Alpine:v3.4: `strongswan` — affected >=0 <5.4.0-r2
- Alpine:v3.5: `strongswan` — affected >=0 <5.5.3-r0
- Alpine:v3.6: `strongswan` — affected >=0 <5.5.3-r0
- Alpine:v3.7: `strongswan` — affected >=0 <5.5.3-r0
- Alpine:v3.8: `strongswan` — affected >=0 <5.5.3-r0
- Alpine:v3.9: `strongswan` — affected >=0 <5.5.3-r0

## Details
The gmp plugin in strongSwan before 5.5.3 does not properly validate RSA public keys before calling mpz_powm_sec, which allows remote peers to cause a denial of service (floating point exception and process crash) via a crafted certificate.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9022
