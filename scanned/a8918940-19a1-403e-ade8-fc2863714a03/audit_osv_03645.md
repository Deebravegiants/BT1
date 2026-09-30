# [H] ALPINE-CVE-2026-3805

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-3805
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-3805
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=8.13.0 <8.19.0-r0
- Alpine:v3.24: `curl` — affected >=8.13.0 <8.19.0-r0

## Details
When doing a second SMB request to the same host again, curl would wrongly use
a data pointer pointing into already freed memory.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-3805
