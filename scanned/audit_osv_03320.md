# [M] ALPINE-CVE-2025-5025

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-5025
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-05-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-5025
Type: osv

## Affected
- Alpine:v3.19: `curl` — affected >=8.5.0 <8.14.0-r0
- Alpine:v3.20: `curl` — affected >=8.5.0 <8.14.0-r0
- Alpine:v3.21: `curl` — affected >=8.5.0 <8.14.0-r0
- Alpine:v3.22: `curl` — affected >=8.5.0 <8.14.0-r0
- Alpine:v3.23: `curl` — affected >=8.5.0 <8.14.0-r0
- Alpine:v3.24: `curl` — affected >=8.5.0 <8.14.0-r0

## Details
libcurl supports *pinning* of the server certificate public key for HTTPS transfers. Due to an omission, this check is not performed when connecting with QUIC for HTTP/3, when the TLS backend is wolfSSL. Documentation says the option works with wolfSSL, failing to specify that it does not for QUIC and HTTP/3. Since pinning makes the transfer succeed if the pin is fine, users could unwittingly connect to an impostor server without noticing.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-5025
