# [H] ALPINE-CVE-2018-16151

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-16151
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-09-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-16151
Type: osv

## Affected
- Alpine:v3.10: `strongswan` — affected >=4.0.0 <5.7.0-r0
- Alpine:v3.11: `strongswan` — affected >=4.0.0 <5.7.0-r0
- Alpine:v3.12: `strongswan` — affected >=4.0.0 <5.7.0-r0
- Alpine:v3.13: `strongswan` — affected >=4.0.0 <5.7.0-r0
- Alpine:v3.14: `strongswan` — affected >=4.0.0 <5.7.0-r0
- Alpine:v3.15: `strongswan` — affected >=4.0.0 <5.7.0-r0
- Alpine:v3.16: `strongswan` — affected >=4.0.0 <5.7.0-r0
- Alpine:v3.17: `strongswan` — affected >=4.0.0 <5.7.0-r0
- Alpine:v3.18: `strongswan` — affected >=4.0.0 <5.7.0-r0
- Alpine:v3.19: `strongswan` — affected >=4.0.0 <5.7.0-r0
- Alpine:v3.20: `strongswan` — affected >=4.0.0 <5.7.0-r0
- Alpine:v3.21: `strongswan` — affected >=4.0.0 <5.7.0-r0
- Alpine:v3.22: `strongswan` — affected >=4.0.0 <5.7.0-r0
- Alpine:v3.23: `strongswan` — affected >=4.0.0 <5.7.0-r0
- Alpine:v3.24: `strongswan` — affected >=4.0.0 <5.7.0-r0
- Alpine:v3.5: `strongswan` — affected >=4.0.0 <5.5.3-r2
- Alpine:v3.6: `strongswan` — affected >=4.0.0 <5.5.3-r2
- Alpine:v3.7: `strongswan` — affected >=4.0.0 <5.6.3-r1
- Alpine:v3.8: `strongswan` — affected >=4.0.0 <5.6.3-r2
- Alpine:v3.9: `strongswan` — affected >=4.0.0 <5.7.0-r0

## Details
In verify_emsa_pkcs1_signature() in gmp_rsa_public_key.c in the gmp plugin in strongSwan 4.x and 5.x before 5.7.0, the RSA implementation based on GMP does not reject excess data after the encoded algorithm OID during PKCS#1 v1.5 signature verification. Similar to the flaw in the same version of strongSwan regarding digestAlgorithm.parameters, a remote attacker can forge signatures when small public exponents are being used, which could lead to impersonation when only an RSA signature is used for IKEv2 authentication.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-16151
