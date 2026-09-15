# [M] ALPINE-CVE-2026-3784

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-3784
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-3784
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.7 <8.19.0-r0
- Alpine:v3.24: `curl` — affected >=7.7 <8.19.0-r0

## Details
curl would wrongly reuse an existing HTTP proxy connection doing CONNECT to a
server, even if the new request uses different credentials for the HTTP proxy.
The proper behavior is to create or use a separate connection.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-3784
