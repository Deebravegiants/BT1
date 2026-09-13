# [H] ALPINE-CVE-2019-3813

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-3813
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-3813
Type: osv

## Affected
- Alpine:v3.10: `spice` — affected >=0.5.2 <0.14.1-r4
- Alpine:v3.11: `spice` — affected >=0.5.2 <0.14.1-r4
- Alpine:v3.12: `spice` — affected >=0.5.2 <0.14.1-r4
- Alpine:v3.13: `spice` — affected >=0.5.2 <0.14.1-r4
- Alpine:v3.14: `spice` — affected >=0.5.2 <0.14.1-r4
- Alpine:v3.15: `spice` — affected >=0.5.2 <0.14.1-r4
- Alpine:v3.16: `spice` — affected >=0.5.2 <0.14.1-r4
- Alpine:v3.17: `spice` — affected >=0.5.2 <0.14.1-r4
- Alpine:v3.18: `spice` — affected >=0.5.2 <0.14.1-r4
- Alpine:v3.19: `spice` — affected >=0.5.2 <0.14.1-r4
- Alpine:v3.20: `spice` — affected >=0.5.2 <0.14.1-r4
- Alpine:v3.21: `spice` — affected >=0.5.2 <0.14.1-r4
- Alpine:v3.22: `spice` — affected >=0.5.2 <0.14.1-r4
- Alpine:v3.23: `spice` — affected >=0.5.2 <0.14.1-r4
- Alpine:v3.24: `spice` — affected >=0.5.2 <0.14.1-r4
- Alpine:v3.6: `spice` — affected >=0.5.2 <0.13.3-r4
- Alpine:v3.7: `spice` — affected >=0.5.2 <0.14.1-r2
- Alpine:v3.8: `spice` — affected >=0.5.2 <0.14.1-r1
- Alpine:v3.9: `spice` — affected >=0.5.2 <0.14.1-r4

## Details
Spice, versions 0.5.2 through 0.14.1, are vulnerable to an out-of-bounds read due to an off-by-one error in memslot_get_virt. This may lead to a denial of service, or, in the worst case, code-execution by unauthenticated attackers.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-3813
