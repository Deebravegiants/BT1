# [C] ALPINE-CVE-2021-3711

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-3711
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3711
Type: osv

## Affected
- Alpine:v3.11: `openssl` — affected >=1.1.1 <1.1.1l-r0
- Alpine:v3.12: `openssl` — affected >=1.1.1 <1.1.1l-r0
- Alpine:v3.13: `openssl` — affected >=1.1.1 <1.1.1l-r0
- Alpine:v3.14: `openssl` — affected >=1.1.1 <1.1.1l-r0
- Alpine:v3.15: `openssl` — affected >=1.1.1 <1.1.1l-r0
- Alpine:v3.16: `openssl` — affected >=1.1.1 <1.1.1l-r0
- Alpine:v3.17: `openssl` — affected >=1.1.1 <1.1.1l-r0
- Alpine:v3.18: `openssl` — affected >=1.1.1 <1.1.1l-r0
- Alpine:v3.19: `openssl` — affected >=1.1.1 <1.1.1l-r0
- Alpine:v3.20: `openssl` — affected >=1.1.1 <1.1.1l-r0
- Alpine:v3.21: `openssl` — affected >=1.1.1 <1.1.1l-r0
- Alpine:v3.22: `openssl` — affected >=1.1.1 <1.1.1l-r0
- Alpine:v3.23: `openssl` — affected >=1.1.1 <1.1.1l-r0
- Alpine:v3.24: `openssl` — affected >=1.1.1 <1.1.1l-r0
- Alpine:v3.15: `openssl3` — affected >=0 <1.1.1l-r0
- Alpine:v3.16: `openssl3` — affected >=0 <1.1.1l-r0

## Details
In order to decrypt SM2 encrypted data an application is expected to call the API function EVP_PKEY_decrypt(). Typically an application will call this function twice. The first time, on entry, the "out" parameter can be NULL and, on exit, the "outlen" parameter is populated with the buffer size required to hold the decrypted plaintext. The application can then allocate a sufficiently sized buffer and call EVP_PKEY_decrypt() again, but this time passing a non-NULL value for the "out" parameter. A bug in the implementation of the SM2 decryption code means that the calculation of the buffer size required to hold the plaintext returned by the first call to EVP_PKEY_decrypt() can be smaller than the actual size required by the second call. This can lead to a buffer overflow when EVP_PKEY_decrypt() is called by the application a second time with a buffer that is too small. A malicious attacker who is able present SM2 content for decryption to an application could cause attacker chosen data to overflow the buffer by up to a maximum of 62 bytes altering the contents of other data held after the buffer, possibly changing application behaviour or causing the application to crash. The location of the buffer is application dependent but is typically heap allocated. Fixed in OpenSSL 1.1.1l (Affected 1.1.1-1.1.1k).

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3711
