# [M] ALPINE-CVE-2025-47905

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-47905
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-05-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-47905
Type: osv

## Affected
- Alpine:v3.21: `varnish` — affected >=0 <7.6.3-r0
- Alpine:v3.22: `varnish` — affected >=0 <7.7.1-r0
- Alpine:v3.23: `varnish` — affected >=0 <7.7.1-r0
- Alpine:v3.24: `varnish` — affected >=0 <7.7.1-r0

## Details
Varnish Cache before 7.6.3 and 7.7 before 7.7.1, and Varnish Enterprise before 6.0.13r14, allow client-side desync via HTTP/1 requests, because the product incorrectly permits CRLF to be skipped to delimit chunk boundaries.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-47905
