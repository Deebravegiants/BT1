# [H] ALPINE-CVE-2022-3924

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-3924
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-3924
Type: osv

## Affected
- Alpine:v3.14: `bind` — affected >=9.16.12 <9.16.37-r0
- Alpine:v3.15: `bind` — affected >=9.16.12 <9.16.37-r0
- Alpine:v3.16: `bind` — affected >=9.16.12 <9.16.37-r0
- Alpine:v3.17: `bind` — affected >=9.16.12 <9.18.11-r0
- Alpine:v3.18: `bind` — affected >=9.16.12 <9.18.11-r0
- Alpine:v3.19: `bind` — affected >=9.16.12 <9.18.11-r0
- Alpine:v3.20: `bind` — affected >=9.16.12 <9.18.11-r0
- Alpine:v3.21: `bind` — affected >=9.16.12 <9.18.11-r0
- Alpine:v3.22: `bind` — affected >=9.16.12 <9.18.11-r0
- Alpine:v3.23: `bind` — affected >=9.16.12 <9.18.11-r0
- Alpine:v3.24: `bind` — affected >=9.16.12 <9.18.11-r0

## Details
This issue can affect BIND 9 resolvers with `stale-answer-enable yes;` that also make use of the option `stale-answer-client-timeout`, configured with a value greater than zero.

If the resolver receives many queries that require recursion, there will be a corresponding increase in the number of clients that are waiting for recursion to complete. If there are sufficient clients already waiting when a new client query is received so that it is necessary to SERVFAIL the longest waiting client (see BIND 9 ARM `recursive-clients` limit and soft quota), then it is possible for a race to occur between providing a stale answer to this older client and sending an early timeout SERVFAIL, which may cause an assertion failure.
This issue affects BIND 9 versions 9.16.12 through 9.16.36, 9.18.0 through 9.18.10, 9.19.0 through 9.19.8, and 9.16.12-S1 through 9.16.36-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-3924
