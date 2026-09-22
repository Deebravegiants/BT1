# [H] ALPINE-CVE-2024-1975

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-1975
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-1975
Type: osv

## Affected
- Alpine:v3.17: `bind` — affected >=0 <9.18.31-r0
- Alpine:v3.18: `bind` — affected >=0 <9.18.31-r0
- Alpine:v3.19: `bind` — affected >=0 <9.18.31-r0
- Alpine:v3.20: `bind` — affected >=0 <9.18.31-r0
- Alpine:v3.21: `bind` — affected >=0 <9.18.28-r0
- Alpine:v3.22: `bind` — affected >=0 <9.18.28-r0
- Alpine:v3.23: `bind` — affected >=0 <9.18.28-r0
- Alpine:v3.24: `bind` — affected >=0 <9.18.28-r0

## Details
If a server hosts a zone containing a "KEY" Resource Record, or a resolver DNSSEC-validates a "KEY" Resource Record from a DNSSEC-signed domain in cache, a client can exhaust resolver CPU resources by sending a stream of SIG(0) signed requests.
This issue affects BIND 9 versions 9.0.0 through 9.11.37, 9.16.0 through 9.16.50, 9.18.0 through 9.18.27, 9.19.0 through 9.19.24, 9.9.3-S1 through 9.11.37-S1, 9.16.8-S1 through 9.16.49-S1, and 9.18.11-S1 through 9.18.27-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-1975
