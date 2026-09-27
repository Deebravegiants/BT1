# [M] ALPINE-CVE-2022-4304

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-4304
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-02-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-4304
Type: osv

## Affected
- Alpine:v3.14: `openssl` — affected >=1.0.2 <1.1.1t-r0
- Alpine:v3.15: `openssl` — affected >=1.0.2 <1.1.1t-r0
- Alpine:v3.16: `openssl` — affected >=1.0.2 <1.1.1t-r0
- Alpine:v3.17: `openssl` — affected >=1.0.2 <3.0.8-r0
- Alpine:v3.18: `openssl` — affected >=1.0.2 <3.0.8-r0
- Alpine:v3.19: `openssl` — affected >=1.0.2 <3.0.8-r0
- Alpine:v3.20: `openssl` — affected >=1.0.2 <3.0.8-r0
- Alpine:v3.21: `openssl` — affected >=1.0.2 <3.0.8-r0
- Alpine:v3.22: `openssl` — affected >=1.0.2 <3.0.8-r0
- Alpine:v3.23: `openssl` — affected >=1.0.2 <3.0.8-r0
- Alpine:v3.24: `openssl` — affected >=1.0.2 <3.0.8-r0
- Alpine:v3.15: `openssl3` — affected >=0 <3.0.8-r0
- Alpine:v3.16: `openssl3` — affected >=0 <3.0.8-r0

## Details
A timing based side channel exists in the OpenSSL RSA Decryption implementation
which could be sufficient to recover a plaintext across a network in a
Bleichenbacher style attack. To achieve a successful decryption an attacker
would have to be able to send a very large number of trial messages for
decryption. The vulnerability affects all RSA padding modes: PKCS#1 v1.5,
RSA-OEAP and RSASVE.

For example, in a TLS connection, RSA is commonly used by a client to send an
encrypted pre-master secret to the server. An attacker that had observed a
genuine connection between a client and a server could use this flaw to send
trial messages to the server and record the time taken to process them. After a
sufficiently large number of messages the attacker could recover the pre-master
secret used for the original connection and thus be able to decrypt the
application data sent over that connection.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-4304
