# [H] ALPINE-CVE-2017-1000381

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-1000381
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-07-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-1000381
Type: osv

## Affected
- Alpine:v3.3: `c-ares` — affected >=0 <1.12.0-r1
- Alpine:v3.4: `c-ares` — affected >=0 <1.12.0-r1
- Alpine:v3.5: `c-ares` — affected >=0 <1.12.0-r1
- Alpine:v3.6: `c-ares` — affected >=0 <1.12.0-r1
- Alpine:v3.10: `nodejs` — affected >=0 <6.11.1-r0
- Alpine:v3.11: `nodejs` — affected >=0 <6.11.1-r0
- Alpine:v3.12: `nodejs` — affected >=0 <6.11.1-r0
- Alpine:v3.13: `nodejs` — affected >=0 <6.11.1-r0
- Alpine:v3.14: `nodejs` — affected >=0 <6.11.1-r0
- Alpine:v3.15: `nodejs` — affected >=0 <6.11.1-r0
- Alpine:v3.16: `nodejs` — affected >=0 <6.11.1-r0
- Alpine:v3.17: `nodejs` — affected >=0 <6.11.1-r0
- Alpine:v3.18: `nodejs` — affected >=0 <6.11.1-r0
- Alpine:v3.19: `nodejs` — affected >=0 <6.11.1-r0
- Alpine:v3.20: `nodejs` — affected >=0 <6.11.1-r0
- Alpine:v3.21: `nodejs` — affected >=0 <6.11.1-r0
- Alpine:v3.22: `nodejs` — affected >=0 <6.11.1-r0
- Alpine:v3.23: `nodejs` — affected >=0 <6.11.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <6.11.1-r0
- Alpine:v3.4: `nodejs` — affected >=0 <6.7.0-r1
- Alpine:v3.5: `nodejs` — affected >=0 <6.9.5-r1
- Alpine:v3.6: `nodejs` — affected >=0 <6.10.3-r1
- Alpine:v3.7: `nodejs` — affected >=0 <6.11.1-r0
- Alpine:v3.8: `nodejs` — affected >=0 <6.11.1-r0
- Alpine:v3.9: `nodejs` — affected >=0 <6.11.1-r0

## Details
The c-ares function `ares_parse_naptr_reply()`, which is used for parsing NAPTR responses, could be triggered to read memory outside of the given input buffer if the passed in DNS response packet was crafted in a particular way.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-1000381
