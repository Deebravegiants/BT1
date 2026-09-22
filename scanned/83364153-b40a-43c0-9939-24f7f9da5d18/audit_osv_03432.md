# [H] ALPINE-CVE-2026-12245

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-12245
Ecosystem: Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-12245
Type: osv

## Affected
- Alpine:v3.24: `nsd` — affected >=4.13.0 <4.14.3-r0

## Details
NSD from version 4.13.0 has a heap use-after-free bug in logging errors on TLS connections, causing a crash of the server process, which can be triggered trivially by sending a DNS query over a DoT connection, and closing the connection without reading the response.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-12245
