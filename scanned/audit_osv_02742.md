# [H] ALPINE-CVE-2023-0217

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-0217
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-0217
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
An invalid pointer dereference on read can be triggered when an
application tries to check a malformed DSA public key by the
EVP_PKEY_public_check() function. This will most likely lead
to an application crash. This function can be called on public
keys supplied from untrusted sources which could allow an attacker
to cause a denial of service attack.

The TLS implementation in OpenSSL does not call this function
but applications might call the function if there are additional
security requirements imposed by standards such as FIPS 140-3.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-0217
