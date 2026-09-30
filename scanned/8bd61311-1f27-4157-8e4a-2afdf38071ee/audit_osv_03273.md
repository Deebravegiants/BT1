# [H] ALPINE-CVE-2025-40775

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-40775
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-40775
Type: osv

## Affected
- Alpine:v3.18: `bind` — affected >=0 <9.18.37-r0
- Alpine:v3.19: `bind` — affected >=0 <9.18.37-r0
- Alpine:v3.20: `bind` — affected >=0 <9.18.37-r0
- Alpine:v3.21: `bind` — affected >=0 <9.18.37-r0
- Alpine:v3.22: `bind` — affected >=0 <9.20.9-r0
- Alpine:v3.23: `bind` — affected >=0 <9.20.9-r0
- Alpine:v3.24: `bind` — affected >=0 <9.20.9-r0

## Details
When an incoming DNS protocol message includes a Transaction Signature (TSIG), BIND always checks it.  If the TSIG contains an invalid value in the algorithm field, BIND immediately aborts with an assertion failure.
This issue affects BIND 9 versions 9.20.0 through 9.20.8 and 9.21.0 through 9.21.7.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-40775
