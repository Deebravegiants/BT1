# [C] ALPINE-CVE-2026-9079

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-9079
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-9079
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=8.8.0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=8.8.0 <8.21.0-r0

## Details
libcurl had a flaw that when instructed to clear proxy authentication
credentials which made it not do so, leaving the old credentials around to get
used for subsequent transfers that should not know nor use them.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-9079
