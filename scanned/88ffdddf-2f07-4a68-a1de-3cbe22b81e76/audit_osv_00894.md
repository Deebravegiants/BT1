# [H] ALPINE-CVE-2018-1058

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-1058
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1058
Type: osv

## Affected
- Alpine:v3.10: `postgresql` — affected >=9.3 <10.3-r0
- Alpine:v3.11: `postgresql` — affected >=9.3 <10.3-r0
- Alpine:v3.12: `postgresql` — affected >=9.3 <10.3-r0
- Alpine:v3.13: `postgresql` — affected >=9.3 <10.3-r0
- Alpine:v3.14: `postgresql` — affected >=9.3 <10.3-r0
- Alpine:v3.4: `postgresql` — affected >=9.3 <9.5.12-r0
- Alpine:v3.5: `postgresql` — affected >=9.3 <9.6.8-r0
- Alpine:v3.6: `postgresql` — affected >=9.3 <9.6.8-r0
- Alpine:v3.7: `postgresql` — affected >=9.3 <10.3-r0
- Alpine:v3.8: `postgresql` — affected >=9.3 <10.3-r0
- Alpine:v3.9: `postgresql` — affected >=9.3 <10.3-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <10.3-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <10.3-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <10.3-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <10.3-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <10.3-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <10.3-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <10.3-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <10.3-r0

## Details
A flaw was found in the way Postgresql allowed a user to modify the behavior of a query for other users. An attacker with a user account could use this flaw to execute code with the permissions of superuser in the database. Versions 9.3 through 10 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1058
