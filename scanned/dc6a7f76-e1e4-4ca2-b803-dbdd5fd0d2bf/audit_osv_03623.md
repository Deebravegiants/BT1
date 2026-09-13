# [H] ALPINE-CVE-2026-34501

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-34501
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-34501
Type: osv

## Affected
- Alpine:v3.21: `apr-util` — affected >=1.6.0 <1.6.4-r0
- Alpine:v3.22: `apr-util` — affected >=1.6.0 <1.6.4-r0
- Alpine:v3.23: `apr-util` — affected >=1.6.0 <1.6.4-r0
- Alpine:v3.24: `apr-util` — affected >=1.6.0 <1.6.4-r0

## Details
Heap-based Buffer Overflow vulnerability in Apache Portable Runtime Utility redis client.

This issue affects Apache Portable Runtime Utility: from 1.6.0 through 1.6.3.

Users are recommended to upgrade to version 1.6.4, which fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-34501
