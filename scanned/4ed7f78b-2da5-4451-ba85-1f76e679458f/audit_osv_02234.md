# [H] ALPINE-CVE-2021-3450

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-3450
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-03-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3450
Type: osv

## Affected
- Alpine:v3.10: `openssl` — affected >=1.1.1h <1.1.1k-r0
- Alpine:v3.11: `openssl` — affected >=1.1.1h <1.1.1k-r0
- Alpine:v3.12: `openssl` — affected >=1.1.1h <1.1.1k-r0
- Alpine:v3.13: `openssl` — affected >=1.1.1h <1.1.1k-r0
- Alpine:v3.14: `openssl` — affected >=1.1.1h <1.1.1k-r0
- Alpine:v3.15: `openssl` — affected >=1.1.1h <1.1.1k-r0
- Alpine:v3.16: `openssl` — affected >=1.1.1h <1.1.1k-r0
- Alpine:v3.17: `openssl` — affected >=1.1.1h <1.1.1k-r0
- Alpine:v3.18: `openssl` — affected >=1.1.1h <1.1.1k-r0
- Alpine:v3.19: `openssl` — affected >=1.1.1h <1.1.1k-r0
- Alpine:v3.20: `openssl` — affected >=1.1.1h <1.1.1k-r0
- Alpine:v3.21: `openssl` — affected >=1.1.1h <1.1.1k-r0
- Alpine:v3.22: `openssl` — affected >=1.1.1h <1.1.1k-r0
- Alpine:v3.23: `openssl` — affected >=1.1.1h <1.1.1k-r0
- Alpine:v3.24: `openssl` — affected >=1.1.1h <1.1.1k-r0
- Alpine:v3.9: `openssl` — affected >=1.1.1h <1.1.1k-r0
- Alpine:v3.15: `openssl3` — affected >=0 <1.1.1k-r0
- Alpine:v3.16: `openssl3` — affected >=0 <1.1.1k-r0

## Details
The X509_V_FLAG_X509_STRICT flag enables additional security checks of the certificates present in a certificate chain. It is not set by default. Starting from OpenSSL version 1.1.1h a check to disallow certificates in the chain that have explicitly encoded elliptic curve parameters was added as an additional strict check. An error in the implementation of this check meant that the result of a previous check to confirm that certificates in the chain are valid CA certificates was overwritten. This effectively bypasses the check that non-CA certificates must not be able to issue other certificates. If a "purpose" has been configured then there is a subsequent opportunity for checks that the certificate is a valid CA. All of the named "purpose" values implemented in libcrypto perform this check. Therefore, where a purpose is set the certificate chain will still be rejected even when the strict flag has been used. A purpose is set by default in libssl client and server certificate verification routines, but it can be overridden or removed by an application. In order to be affected, an application must explicitly set the X509_V_FLAG_X509_STRICT verification flag and either not set a purpose for the certificate verification or, in the case of TLS client or server applications, override the default purpose. OpenSSL versions 1.1.1h and newer are affected by this issue. Users of these versions should upgrade to OpenSSL 1.1.1k. OpenSSL 1.0.2 is not impacted by this issue. Fixed in OpenSSL 1.1.1k (Affected 1.1.1h-1.1.1j).

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3450
