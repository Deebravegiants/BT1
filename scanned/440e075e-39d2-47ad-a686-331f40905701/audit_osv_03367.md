# [M] ALPINE-CVE-2025-62408

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-62408
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-62408
Type: osv

## Affected
- Alpine:v3.21: `c-ares` — affected >=1.32.3 <1.34.6-r0
- Alpine:v3.22: `c-ares` — affected >=1.32.3 <1.34.6-r0
- Alpine:v3.23: `c-ares` — affected >=1.32.3 <1.34.6-r0
- Alpine:v3.24: `c-ares` — affected >=1.32.3 <1.34.6-r0

## Details
c-ares is an asynchronous resolver library. Versions 1.32.3 through 1.34.5  terminate a query after maximum attempts when using read_answer() and process_answer(), which can cause a Denial of Service. This issue is fixed in version 1.34.6.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-62408
