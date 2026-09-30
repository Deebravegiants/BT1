# [M] ALPINE-CVE-2023-1255

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-1255
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-1255
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=3.0.0 <3.0.8-r4
- Alpine:v3.18: `openssl` — affected >=3.0.0 <3.1.0-r4
- Alpine:v3.19: `openssl` — affected >=3.0.0 <3.1.0-r4
- Alpine:v3.20: `openssl` — affected >=3.0.0 <3.1.0-r4
- Alpine:v3.21: `openssl` — affected >=3.0.0 <3.1.0-r4
- Alpine:v3.22: `openssl` — affected >=3.0.0 <3.1.0-r4
- Alpine:v3.23: `openssl` — affected >=3.0.0 <3.1.0-r4
- Alpine:v3.24: `openssl` — affected >=3.0.0 <3.1.0-r4
- Alpine:v3.15: `openssl3` — affected >=0 <3.0.8-r3
- Alpine:v3.16: `openssl3` — affected >=0 <3.0.8-r3

## Details
Issue summary: The AES-XTS cipher decryption implementation for 64 bit ARM
platform contains a bug that could cause it to read past the input buffer,
leading to a crash.

Impact summary: Applications that use the AES-XTS algorithm on the 64 bit ARM
platform can crash in rare circumstances. The AES-XTS algorithm is usually
used for disk encryption.

The AES-XTS cipher decryption implementation for 64 bit ARM platform will read
past the end of the ciphertext buffer if the ciphertext size is 4 mod 5 in 16
byte blocks, e.g. 144 bytes or 1024 bytes. If the memory after the ciphertext
buffer is unmapped, this will trigger a crash which results in a denial of
service.

If an attacker can control the size and location of the ciphertext buffer
being decrypted by an application using AES-XTS on 64 bit ARM, the
application is affected. This is fairly unlikely making this issue
a Low severity one.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-1255
