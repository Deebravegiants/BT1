# [H] ALPINE-CVE-2022-0778

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-0778
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-03-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-0778
Type: osv

## Affected
- Alpine:v3.14: `libretls` — affected >=0 <3.3.3p1-r3
- Alpine:v3.15: `libretls` — affected >=0 <3.3.4-r3
- Alpine:v3.16: `libretls` — affected >=0 <3.5.1-r0
- Alpine:v3.17: `libretls` — affected >=0 <3.5.1-r0
- Alpine:v3.18: `libretls` — affected >=0 <3.5.1-r0
- Alpine:v3.19: `libretls` — affected >=0 <3.5.1-r0
- Alpine:v3.20: `libretls` — affected >=0 <3.5.1-r0
- Alpine:v3.21: `libretls` — affected >=0 <3.5.1-r0
- Alpine:v3.22: `libretls` — affected >=0 <3.5.1-r0
- Alpine:v3.12: `openssl` — affected >=1.0.2 <1.1.1n-r0
- Alpine:v3.13: `openssl` — affected >=1.0.2 <1.1.1n-r0
- Alpine:v3.14: `openssl` — affected >=1.0.2 <1.1.1n-r0
- Alpine:v3.15: `openssl` — affected >=1.0.2 <1.1.1n-r0
- Alpine:v3.16: `openssl` — affected >=1.0.2 <1.1.1n-r0
- Alpine:v3.17: `openssl` — affected >=1.0.2 <3.0.2-r0
- Alpine:v3.18: `openssl` — affected >=1.0.2 <3.0.2-r0
- Alpine:v3.19: `openssl` — affected >=1.0.2 <3.0.2-r0
- Alpine:v3.20: `openssl` — affected >=1.0.2 <3.0.2-r0
- Alpine:v3.21: `openssl` — affected >=1.0.2 <3.0.2-r0
- Alpine:v3.22: `openssl` — affected >=1.0.2 <3.0.2-r0
- Alpine:v3.23: `openssl` — affected >=1.0.2 <3.0.2-r0
- Alpine:v3.24: `openssl` — affected >=1.0.2 <3.0.2-r0
- Alpine:v3.15: `openssl3` — affected >=0 <3.0.2-r0
- Alpine:v3.16: `openssl3` — affected >=0 <3.0.2-r0

## Details
The BN_mod_sqrt() function, which computes a modular square root, contains a bug that can cause it to loop forever for non-prime moduli. Internally this function is used when parsing certificates that contain elliptic curve public keys in compressed form or explicit elliptic curve parameters with a base point encoded in compressed form. It is possible to trigger the infinite loop by crafting a certificate that has invalid explicit curve parameters. Since certificate parsing happens prior to verification of the certificate signature, any process that parses an externally supplied certificate may thus be subject to a denial of service attack. The infinite loop can also be reached when parsing crafted private keys as they can contain explicit elliptic curve parameters. Thus vulnerable situations include: - TLS clients consuming server certificates - TLS servers consuming client certificates - Hosting providers taking certificates or private keys from customers - Certificate authorities parsing certification requests from subscribers - Anything else which parses ASN.1 elliptic curve parameters Also any other applications that use the BN_mod_sqrt() where the attacker can control the parameter values are vulnerable to this DoS issue. In the OpenSSL 1.0.2 version the public key is not parsed during initial parsing of the certificate which makes it slightly harder to trigger the infinite loop. However any operation which requires the public key from the certificate will trigger the infinite loop. In particular the attacker can use a self-signed certificate to trigger the loop during verification of the certificate signature. This issue affects OpenSSL versions 1.0.2, 1.1.1 and 3.0. It was addressed in the releases of 1.1.1n and 3.0.2 on the 15th March 2022. Fixed in OpenSSL 3.0.2 (Affected 3.0.0,3.0.1). Fixed in OpenSSL 1.1.1n (Affected 1.1.1-1.1.1m). Fixed in OpenSSL 1.0.2zd (Affected 1.0.2-1.0.2zc).

## References
- https://security.alpinelinux.org/vuln/CVE-2022-0778
