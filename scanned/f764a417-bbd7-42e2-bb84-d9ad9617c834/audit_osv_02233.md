# [M] ALPINE-CVE-2021-3449

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-3449
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3449
Type: osv

## Affected
- Alpine:v3.10: `openssl` — affected >=1.1.1 <1.1.1k-r0
- Alpine:v3.11: `openssl` — affected >=1.1.1 <1.1.1k-r0
- Alpine:v3.12: `openssl` — affected >=1.1.1 <1.1.1k-r0
- Alpine:v3.13: `openssl` — affected >=1.1.1 <1.1.1k-r0
- Alpine:v3.14: `openssl` — affected >=1.1.1 <1.1.1k-r0
- Alpine:v3.15: `openssl` — affected >=1.1.1 <1.1.1k-r0
- Alpine:v3.16: `openssl` — affected >=1.1.1 <1.1.1k-r0
- Alpine:v3.17: `openssl` — affected >=1.1.1 <1.1.1k-r0
- Alpine:v3.18: `openssl` — affected >=1.1.1 <1.1.1k-r0
- Alpine:v3.19: `openssl` — affected >=1.1.1 <1.1.1k-r0
- Alpine:v3.20: `openssl` — affected >=1.1.1 <1.1.1k-r0
- Alpine:v3.21: `openssl` — affected >=1.1.1 <1.1.1k-r0
- Alpine:v3.22: `openssl` — affected >=1.1.1 <1.1.1k-r0
- Alpine:v3.23: `openssl` — affected >=1.1.1 <1.1.1k-r0
- Alpine:v3.24: `openssl` — affected >=1.1.1 <1.1.1k-r0
- Alpine:v3.9: `openssl` — affected >=1.1.1 <1.1.1k-r0
- Alpine:v3.15: `openssl3` — affected >=0 <1.1.1k-r0
- Alpine:v3.16: `openssl3` — affected >=0 <1.1.1k-r0

## Details
An OpenSSL TLS server may crash if sent a maliciously crafted renegotiation ClientHello message from a client. If a TLSv1.2 renegotiation ClientHello omits the signature_algorithms extension (where it was present in the initial ClientHello), but includes a signature_algorithms_cert extension then a NULL pointer dereference will result, leading to a crash and a denial of service attack. A server is only vulnerable if it has TLSv1.2 and renegotiation enabled (which is the default configuration). OpenSSL TLS clients are not impacted by this issue. All OpenSSL 1.1.1 versions are affected by this issue. Users of these versions should upgrade to OpenSSL 1.1.1k. OpenSSL 1.0.2 is not impacted by this issue. Fixed in OpenSSL 1.1.1k (Affected 1.1.1-1.1.1j).

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3449
