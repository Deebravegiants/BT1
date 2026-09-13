# [H] ALPINE-CVE-2023-0401

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-0401
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-0401
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=3.0.0 <3.0.8-r0
- Alpine:v3.18: `openssl` — affected >=3.0.0 <3.0.8-r0
- Alpine:v3.19: `openssl` — affected >=3.0.0 <3.0.8-r0
- Alpine:v3.20: `openssl` — affected >=3.0.0 <3.0.8-r0
- Alpine:v3.21: `openssl` — affected >=3.0.0 <3.0.8-r0
- Alpine:v3.22: `openssl` — affected >=3.0.0 <3.0.8-r0
- Alpine:v3.23: `openssl` — affected >=3.0.0 <3.0.8-r0
- Alpine:v3.24: `openssl` — affected >=3.0.0 <3.0.8-r0
- Alpine:v3.15: `openssl3` — affected >=0 <3.0.8-r0
- Alpine:v3.16: `openssl3` — affected >=0 <3.0.8-r0

## Details
A NULL pointer can be dereferenced when signatures are being
verified on PKCS7 signed or signedAndEnveloped data. In case the hash
algorithm used for the signature is known to the OpenSSL library but
the implementation of the hash algorithm is not available the digest
initialization will fail. There is a missing check for the return
value from the initialization function which later leads to invalid
usage of the digest API most likely leading to a crash.

The unavailability of an algorithm can be caused by using FIPS
enabled configuration of providers or more commonly by not loading
the legacy provider.

PKCS7 data is processed by the SMIME library calls and also by the
time stamp (TS) library calls. The TLS implementation in OpenSSL does
not call these functions however third party applications would be
affected if they call these functions to verify signatures on untrusted
data.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-0401
