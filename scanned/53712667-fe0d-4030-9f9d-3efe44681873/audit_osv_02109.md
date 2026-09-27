# [H] ALPINE-CVE-2021-23840

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-23840
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-23840
Type: osv

## Affected
- Alpine:v3.10: `openssl` — affected >=1.0.2 <1.1.1j-r0
- Alpine:v3.11: `openssl` — affected >=1.0.2 <1.1.1j-r0
- Alpine:v3.12: `openssl` — affected >=1.0.2 <1.1.1j-r0
- Alpine:v3.13: `openssl` — affected >=1.0.2 <1.1.1j-r0
- Alpine:v3.14: `openssl` — affected >=1.0.2 <1.1.1j-r0
- Alpine:v3.15: `openssl` — affected >=1.0.2 <1.1.1j-r0
- Alpine:v3.16: `openssl` — affected >=1.0.2 <1.1.1j-r0
- Alpine:v3.17: `openssl` — affected >=1.0.2 <1.1.1j-r0
- Alpine:v3.18: `openssl` — affected >=1.0.2 <1.1.1j-r0
- Alpine:v3.19: `openssl` — affected >=1.0.2 <1.1.1j-r0
- Alpine:v3.20: `openssl` — affected >=1.0.2 <1.1.1j-r0
- Alpine:v3.21: `openssl` — affected >=1.0.2 <1.1.1j-r0
- Alpine:v3.22: `openssl` — affected >=1.0.2 <1.1.1j-r0
- Alpine:v3.23: `openssl` — affected >=1.0.2 <1.1.1j-r0
- Alpine:v3.24: `openssl` — affected >=1.0.2 <1.1.1j-r0
- Alpine:v3.9: `openssl` — affected >=1.0.2 <1.1.1j-r0
- Alpine:v3.15: `openssl3` — affected >=0 <1.1.1j-r0
- Alpine:v3.16: `openssl3` — affected >=0 <1.1.1j-r0

## Details
Calls to EVP_CipherUpdate, EVP_EncryptUpdate and EVP_DecryptUpdate may overflow the output length argument in some cases where the input length is close to the maximum permissable length for an integer on the platform. In such cases the return value from the function call will be 1 (indicating success), but the output length value will be negative. This could cause applications to behave incorrectly or crash. OpenSSL versions 1.1.1i and below are affected by this issue. Users of these versions should upgrade to OpenSSL 1.1.1j. OpenSSL versions 1.0.2x and below are affected by this issue. However OpenSSL 1.0.2 is out of support and no longer receiving public updates. Premium support customers of OpenSSL 1.0.2 should upgrade to 1.0.2y. Other users should upgrade to 1.1.1j. Fixed in OpenSSL 1.1.1j (Affected 1.1.1-1.1.1i). Fixed in OpenSSL 1.0.2y (Affected 1.0.2-1.0.2x).

## References
- https://security.alpinelinux.org/vuln/CVE-2021-23840
