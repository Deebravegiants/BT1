# [M] ALPINE-CVE-2024-4603

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-4603
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-05-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-4603
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=0 <3.0.13-r0
- Alpine:v3.18: `openssl` — affected >=0 <3.1.5-r0
- Alpine:v3.19: `openssl` — affected >=0 <3.1.5-r0
- Alpine:v3.20: `openssl` — affected >=0 <3.3.0-r2
- Alpine:v3.21: `openssl` — affected >=0 <3.3.0-r2
- Alpine:v3.22: `openssl` — affected >=0 <3.3.0-r2
- Alpine:v3.23: `openssl` — affected >=0 <3.3.0-r2
- Alpine:v3.24: `openssl` — affected >=0 <3.3.0-r2

## Details
Issue summary: Checking excessively long DSA keys or parameters may be very
slow.

Impact summary: Applications that use the functions EVP_PKEY_param_check()
or EVP_PKEY_public_check() to check a DSA public key or DSA parameters may
experience long delays. Where the key or parameters that are being checked
have been obtained from an untrusted source this may lead to a Denial of
Service.

The functions EVP_PKEY_param_check() or EVP_PKEY_public_check() perform
various checks on DSA parameters. Some of those computations take a long time
if the modulus (`p` parameter) is too large.

Trying to use a very large modulus is slow and OpenSSL will not allow using
public keys with a modulus which is over 10,000 bits in length for signature
verification. However the key and parameter check functions do not limit
the modulus size when performing the checks.

An application that calls EVP_PKEY_param_check() or EVP_PKEY_public_check()
and supplies a key or parameters obtained from an untrusted source could be
vulnerable to a Denial of Service attack.

These functions are not called by OpenSSL itself on untrusted DSA keys so
only applications that directly call these functions may be vulnerable.

Also vulnerable are the OpenSSL pkey and pkeyparam command line applications
when using the `-check` option.

The OpenSSL SSL/TLS implementation is not affected by this issue.

The OpenSSL 3.0 and 3.1 FIPS providers are affected by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-4603
