# [H] ALPINE-CVE-2025-40776

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-40776
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2025-07-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-40776
Type: osv

## Affected
- Alpine:v3.22: `bind` — affected >=0 <9.20.11-r0
- Alpine:v3.23: `bind` — affected >=0 <9.20.11-r0
- Alpine:v3.24: `bind` — affected >=0 <9.20.11-r0

## Details
A `named` caching resolver that is configured to send ECS (EDNS Client Subnet) options may be vulnerable to a cache-poisoning attack.
This issue affects BIND 9 versions 9.11.3-S1 through 9.16.50-S1, 9.18.11-S1 through 9.18.37-S1, and 9.20.9-S1 through 9.20.10-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-40776
