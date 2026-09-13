# [H] ALPINE-CVE-2026-5946

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-5946
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-5946
Type: osv

## Affected
- Alpine:v3.20: `bind` — affected >=9.11.0 <9.18.49-r0
- Alpine:v3.21: `bind` — affected >=9.11.0 <9.18.49-r0
- Alpine:v3.22: `bind` — affected >=9.11.0 <9.20.23-r0
- Alpine:v3.23: `bind` — affected >=9.11.0 <9.20.23-r0
- Alpine:v3.24: `bind` — affected >=9.11.0 <9.20.23-r0

## Details
Multiple flaws have been identified in `named` related to the handling of DNS messages whose CLASS is not Internet (`IN`) — for example, `CHAOS` or `HESIOD`, or DNS messages that specify meta-classes (`ANY` or `NONE`) in the question section. Specially crafted requests reaching the affected code paths — recursion, dynamic updates (`UPDATE`), zone change notifications (`NOTIFY`), or processing of `IN`-specific record types in non-`IN` data — can cause assertion failures in `named`.
This issue affects BIND 9 versions 9.11.0 through 9.16.50, 9.18.0 through 9.18.48, 9.20.0 through 9.20.22, 9.21.0 through 9.21.21, 9.11.3-S1 through 9.16.50-S1, 9.18.11-S1 through 9.18.48-S1, and 9.20.9-S1 through 9.20.22-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-5946
