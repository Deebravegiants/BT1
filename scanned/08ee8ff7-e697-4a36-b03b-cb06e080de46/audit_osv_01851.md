# [H] ALPINE-CVE-2020-1967

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-1967
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-04-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-1967
Type: osv

## Affected
- Alpine:v3.10: `openssl` — affected >=1.1.1d <1.1.1g-r0
- Alpine:v3.11: `openssl` — affected >=1.1.1d <1.1.1g-r0
- Alpine:v3.12: `openssl` — affected >=1.1.1d <1.1.1g-r0
- Alpine:v3.13: `openssl` — affected >=1.1.1d <1.1.1g-r0
- Alpine:v3.14: `openssl` — affected >=1.1.1d <1.1.1g-r0
- Alpine:v3.15: `openssl` — affected >=1.1.1d <1.1.1g-r0
- Alpine:v3.16: `openssl` — affected >=1.1.1d <1.1.1g-r0
- Alpine:v3.17: `openssl` — affected >=1.1.1d <1.1.1g-r0
- Alpine:v3.18: `openssl` — affected >=1.1.1d <1.1.1g-r0
- Alpine:v3.19: `openssl` — affected >=1.1.1d <1.1.1g-r0
- Alpine:v3.20: `openssl` — affected >=1.1.1d <1.1.1g-r0
- Alpine:v3.21: `openssl` — affected >=1.1.1d <1.1.1g-r0
- Alpine:v3.22: `openssl` — affected >=1.1.1d <1.1.1g-r0
- Alpine:v3.23: `openssl` — affected >=1.1.1d <1.1.1g-r0
- Alpine:v3.24: `openssl` — affected >=1.1.1d <1.1.1g-r0
- Alpine:v3.9: `openssl` — affected >=1.1.1d <1.1.1g-r0
- Alpine:v3.15: `openssl3` — affected >=0 <1.1.1g-r0
- Alpine:v3.16: `openssl3` — affected >=0 <1.1.1g-r0

## Details
Server or client applications that call the SSL_check_chain() function during or after a TLS 1.3 handshake may crash due to a NULL pointer dereference as a result of incorrect handling of the "signature_algorithms_cert" TLS extension. The crash occurs if an invalid or unrecognised signature algorithm is received from the peer. This could be exploited by a malicious peer in a Denial of Service attack. OpenSSL version 1.1.1d, 1.1.1e, and 1.1.1f are affected by this issue. This issue did not affect OpenSSL versions prior to 1.1.1d. Fixed in OpenSSL 1.1.1g (Affected 1.1.1d-1.1.1f).

## References
- https://security.alpinelinux.org/vuln/CVE-2020-1967
