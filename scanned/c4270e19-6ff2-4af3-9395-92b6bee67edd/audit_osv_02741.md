# [H] ALPINE-CVE-2023-0216

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-0216
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-0216
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
application tries to load malformed PKCS7 data with the
d2i_PKCS7(), d2i_PKCS7_bio() or d2i_PKCS7_fp() functions.

The result of the dereference is an application crash which could
lead to a denial of service attack. The TLS implementation in OpenSSL
does not call this function however third party applications might
call these functions on untrusted data.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-0216
