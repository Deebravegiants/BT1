# [H] ALPINE-CVE-2025-40777

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-40777
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-40777
Type: osv

## Affected
- Alpine:v3.22: `bind` — affected >=0 <9.20.11-r0
- Alpine:v3.23: `bind` — affected >=0 <9.20.11-r0
- Alpine:v3.24: `bind` — affected >=0 <9.20.11-r0

## Details
If a `named` caching resolver is configured with `serve-stale-enable` `yes`, and with `stale-answer-client-timeout` set to `0` (the only allowable value other than `disabled`), and if the resolver, in the process of resolving a query, encounters a CNAME chain involving a specific combination of cached or authoritative records, the daemon will abort with an assertion failure.
This issue affects BIND 9 versions 9.20.0 through 9.20.10, 9.21.0 through 9.21.9, and 9.20.9-S1 through 9.20.10-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-40777
