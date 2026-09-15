# [M] ALPINE-CVE-2025-4947

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-4947
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-05-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-4947
Type: osv

## Affected
- Alpine:v3.19: `curl` — affected >=8.8.0 <8.14.0-r0
- Alpine:v3.20: `curl` — affected >=8.8.0 <8.14.0-r0
- Alpine:v3.21: `curl` — affected >=8.8.0 <8.14.0-r0
- Alpine:v3.22: `curl` — affected >=8.8.0 <8.14.0-r0
- Alpine:v3.23: `curl` — affected >=8.8.0 <8.14.0-r0
- Alpine:v3.24: `curl` — affected >=8.8.0 <8.14.0-r0

## Details
libcurl accidentally skips the certificate verification for QUIC connections when connecting to a host specified as an IP address in the URL. Therefore, it does not detect impostors or man-in-the-middle attacks.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-4947
