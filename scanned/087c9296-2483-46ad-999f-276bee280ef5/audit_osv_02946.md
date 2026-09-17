# [H] ALPINE-CVE-2023-5517

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-5517
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-5517
Type: osv

## Affected
- Alpine:v3.16: `bind` — affected >=9.12.0 <9.16.48-r0
- Alpine:v3.17: `bind` — affected >=9.12.0 <9.18.24-r0
- Alpine:v3.18: `bind` — affected >=9.12.0 <9.18.24-r0
- Alpine:v3.19: `bind` — affected >=9.12.0 <9.18.24-r0
- Alpine:v3.20: `bind` — affected >=9.12.0 <9.18.24-r0
- Alpine:v3.21: `bind` — affected >=9.12.0 <9.18.24-r0
- Alpine:v3.22: `bind` — affected >=9.12.0 <9.18.24-r0
- Alpine:v3.23: `bind` — affected >=9.12.0 <9.18.24-r0
- Alpine:v3.24: `bind` — affected >=9.12.0 <9.18.24-r0

## Details
A flaw in query-handling code can cause `named` to exit prematurely with an assertion failure when:

  - `nxdomain-redirect <domain>;` is configured, and
  - the resolver receives a PTR query for an RFC 1918 address that would normally result in an authoritative NXDOMAIN response.
This issue affects BIND 9 versions 9.12.0 through 9.16.45, 9.18.0 through 9.18.21, 9.19.0 through 9.19.19, 9.16.8-S1 through 9.16.45-S1, and 9.18.11-S1 through 9.18.21-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-5517
