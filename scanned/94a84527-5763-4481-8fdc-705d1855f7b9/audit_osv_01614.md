# [M] ALPINE-CVE-2019-6133

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-6133
Ecosystem: Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-01-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-6133
Type: osv

## Affected
- Alpine:v3.7: `polkit` — affected >=0 <0.105-r10
- Alpine:v3.8: `polkit` — affected >=0 <0.105-r11
- Alpine:v3.9: `polkit` — affected >=0 <0.105-r11

## Details
In PolicyKit (aka polkit) 0.115, the "start time" protection mechanism can be bypassed because fork() is not atomic, and therefore authorization decisions are improperly cached. This is related to lack of uid checking in polkitbackend/polkitbackendinteractiveauthority.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-6133
