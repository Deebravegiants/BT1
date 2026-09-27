# [M] ALPINE-CVE-2023-6237

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-6237
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-6237
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=0 <3.0.12-r3
- Alpine:v3.18: `openssl` — affected >=0 <3.1.4-r4
- Alpine:v3.19: `openssl` — affected >=0 <3.1.4-r4
- Alpine:v3.20: `openssl` — affected >=0 <3.1.4-r4
- Alpine:v3.21: `openssl` — affected >=0 <3.1.4-r4
- Alpine:v3.22: `openssl` — affected >=0 <3.1.4-r4
- Alpine:v3.23: `openssl` — affected >=0 <3.1.4-r4
- Alpine:v3.24: `openssl` — affected >=0 <3.1.4-r4

## Details
Issue summary: Checking excessively long invalid RSA public keys may take
a long time.

Impact summary: Applications that use the function EVP_PKEY_public_check()
to check RSA public keys may experience long delays. Where the key that
is being checked has been obtained from an untrusted source this may lead
to a Denial of Service.

When function EVP_PKEY_public_check() is called on RSA public keys,
a computation is done to confirm that the RSA modulus, n, is composite.
For valid RSA keys, n is a product of two or more large primes and this
computation completes quickly. However, if n is an overly large prime,
then this computation would take a long time.

An application that calls EVP_PKEY_public_check() and supplies an RSA key
obtained from an untrusted source could be vulnerable to a Denial of Service
attack.

The function EVP_PKEY_public_check() is not called from other OpenSSL
functions however it is called from the OpenSSL pkey command line
application. For that reason that application is also vulnerable if used
with the '-pubin' and '-check' options on untrusted data.

The OpenSSL SSL/TLS implementation is not affected by this issue.

The OpenSSL 3.0 and 3.1 FIPS providers are affected by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-6237
