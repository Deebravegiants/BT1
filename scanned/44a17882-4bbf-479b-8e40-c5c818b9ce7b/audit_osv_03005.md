# [M] ALPINE-CVE-2024-2379

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-2379
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-03-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-2379
Type: osv

## Affected
- Alpine:v3.17: `curl` — affected >=0 <8.7.1-r0
- Alpine:v3.18: `curl` — affected >=0 <8.7.1-r0
- Alpine:v3.19: `curl` — affected >=0 <8.7.1-r0
- Alpine:v3.20: `curl` — affected >=0 <8.7.1-r0
- Alpine:v3.21: `curl` — affected >=0 <8.7.1-r0
- Alpine:v3.22: `curl` — affected >=0 <8.7.1-r0
- Alpine:v3.23: `curl` — affected >=0 <8.7.1-r0
- Alpine:v3.24: `curl` — affected >=0 <8.7.1-r0

## Details
libcurl skips the certificate verification for a QUIC connection under certain conditions, when built to use wolfSSL. If told to use an unknown/bad cipher or curve, the error path accidentally skips the verification and returns OK, thus ignoring any certificate problems.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-2379
