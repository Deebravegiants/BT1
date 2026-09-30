# [M] ALPINE-CVE-2021-25219

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-25219
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2021-10-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-25219
Type: osv

## Affected
- Alpine:v3.12: `bind` — affected >=9.3.0 <9.16.27-r0
- Alpine:v3.13: `bind` — affected >=9.3.0 <9.16.25-r0
- Alpine:v3.14: `bind` — affected >=9.3.0 <9.16.25-r0
- Alpine:v3.15: `bind` — affected >=9.3.0 <9.16.22-r0
- Alpine:v3.16: `bind` — affected >=9.3.0 <9.16.22-r0
- Alpine:v3.17: `bind` — affected >=9.3.0 <9.16.22-r0
- Alpine:v3.18: `bind` — affected >=9.3.0 <9.16.22-r0
- Alpine:v3.19: `bind` — affected >=9.3.0 <9.16.22-r0
- Alpine:v3.20: `bind` — affected >=9.3.0 <9.16.22-r0
- Alpine:v3.21: `bind` — affected >=9.3.0 <9.16.22-r0
- Alpine:v3.22: `bind` — affected >=9.3.0 <9.16.22-r0
- Alpine:v3.23: `bind` — affected >=9.3.0 <9.16.22-r0
- Alpine:v3.24: `bind` — affected >=9.3.0 <9.16.22-r0

## Details
In BIND 9.3.0 -> 9.11.35, 9.12.0 -> 9.16.21, and versions 9.9.3-S1 -> 9.11.35-S1 and 9.16.8-S1 -> 9.16.21-S1 of BIND Supported Preview Edition, as well as release versions 9.17.0 -> 9.17.18 of the BIND 9.17 development branch, exploitation of broken authoritative servers using a flaw in response processing can cause degradation in BIND resolver performance. The way the lame cache is currently designed makes it possible for its internal data structures to grow almost infinitely, which may cause significant delays in client query processing.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-25219
