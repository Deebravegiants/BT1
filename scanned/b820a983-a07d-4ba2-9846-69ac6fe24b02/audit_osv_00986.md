# [H] ALPINE-CVE-2018-14553

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-14553
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-14553
Type: osv

## Affected
- Alpine:v3.10: `gd` — affected >=0 <2.2.5-r3
- Alpine:v3.11: `gd` — affected >=0 <2.2.5-r3
- Alpine:v3.12: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.13: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.14: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.15: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.16: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.17: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.18: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.19: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.20: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.21: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.22: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.23: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.24: `gd` — affected >=0 <2.3.0-r0
- Alpine:v3.8: `gd` — affected >=0 <2.2.5-r3
- Alpine:v3.9: `gd` — affected >=0 <2.2.5-r3

## Details
gdImageClone in gd.c in libgd 2.1.0-rc2 through 2.2.5 has a NULL pointer dereference allowing attackers to crash an application via a specific function call sequence. Only affects PHP when linked with an external libgd (not bundled).

## References
- https://security.alpinelinux.org/vuln/CVE-2018-14553
