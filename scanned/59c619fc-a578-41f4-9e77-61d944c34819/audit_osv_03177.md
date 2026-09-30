# [H] ALPINE-CVE-2025-0725

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-0725
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-02-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-0725
Type: osv

## Affected
- Alpine:v3.18: `curl` — affected >=7.10.5 <8.12.0-r0
- Alpine:v3.19: `curl` — affected >=7.10.5 <8.12.0-r0
- Alpine:v3.20: `curl` — affected >=7.10.5 <8.12.0-r0
- Alpine:v3.21: `curl` — affected >=7.10.5 <8.12.0-r0
- Alpine:v3.22: `curl` — affected >=7.10.5 <8.12.0-r0
- Alpine:v3.23: `curl` — affected >=7.10.5 <8.12.0-r0
- Alpine:v3.24: `curl` — affected >=7.10.5 <8.12.0-r0

## Details
When libcurl is asked to perform automatic gzip decompression of
content-encoded HTTP responses with the `CURLOPT_ACCEPT_ENCODING` option,
**using zlib 1.2.0.3 or older**, an attacker-controlled integer overflow would
make libcurl perform a buffer overflow.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-0725
