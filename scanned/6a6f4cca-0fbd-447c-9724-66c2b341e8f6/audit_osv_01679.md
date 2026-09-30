# [M] ALPINE-CVE-2019-9516

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-9516
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-9516
Type: osv

## Affected
- Alpine:v3.10: `nginx` — affected >=1.9.5 <1.16.1-r0
- Alpine:v3.11: `nginx` — affected >=1.9.5 <1.16.1-r0
- Alpine:v3.12: `nginx` — affected >=1.9.5 <1.16.1-r0
- Alpine:v3.13: `nginx` — affected >=1.9.5 <1.16.1-r0
- Alpine:v3.14: `nginx` — affected >=1.9.5 <1.16.1-r0
- Alpine:v3.15: `nginx` — affected >=1.9.5 <1.16.1-r0
- Alpine:v3.16: `nginx` — affected >=1.9.5 <1.16.1-r0
- Alpine:v3.17: `nginx` — affected >=1.9.5 <1.16.1-r0
- Alpine:v3.18: `nginx` — affected >=1.9.5 <1.16.1-r0
- Alpine:v3.19: `nginx` — affected >=1.9.5 <1.16.1-r0
- Alpine:v3.20: `nginx` — affected >=1.9.5 <1.16.1-r0
- Alpine:v3.21: `nginx` — affected >=1.9.5 <1.16.1-r0
- Alpine:v3.22: `nginx` — affected >=1.9.5 <1.16.1-r0
- Alpine:v3.23: `nginx` — affected >=1.9.5 <1.16.1-r0
- Alpine:v3.24: `nginx` — affected >=1.9.5 <1.16.1-r0
- Alpine:v3.8: `nginx` — affected >=1.9.5 <1.14.1-r1
- Alpine:v3.9: `nginx` — affected >=1.9.5 <1.14.1-r2
- Alpine:v3.10: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.11: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.12: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.13: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.14: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.15: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.16: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.17: `nodejs` — affected >=0 <10.16.3-r0

## Details
Some HTTP/2 implementations are vulnerable to a header leak, potentially leading to a denial of service. The attacker sends a stream of headers with a 0-length header name and 0-length header value, optionally Huffman encoded into 1-byte or greater headers. Some implementations allocate memory for these headers and keep the allocation alive until the session dies. This can consume excess memory.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-9516
