# [H] ALPINE-CVE-2017-7548

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-7548
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-08-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7548
Type: osv

## Affected
- Alpine:v3.10: `postgresql` — affected >=9.4 <9.6.4-r0
- Alpine:v3.11: `postgresql` — affected >=9.4 <9.6.4-r0
- Alpine:v3.12: `postgresql` — affected >=9.4 <9.6.4-r0
- Alpine:v3.13: `postgresql` — affected >=9.4 <9.6.4-r0
- Alpine:v3.14: `postgresql` — affected >=9.4 <9.6.4-r0
- Alpine:v3.3: `postgresql` — affected >=9.4 <9.4.13-r0
- Alpine:v3.4: `postgresql` — affected >=9.4 <9.5.8-r0
- Alpine:v3.5: `postgresql` — affected >=9.4 <9.6.4-r0
- Alpine:v3.6: `postgresql` — affected >=9.4 <9.6.4-r0
- Alpine:v3.7: `postgresql` — affected >=9.4 <9.6.4-r0
- Alpine:v3.8: `postgresql` — affected >=9.4 <9.6.4-r0
- Alpine:v3.9: `postgresql` — affected >=9.4 <9.6.4-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <9.6.4-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <9.6.4-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <9.6.4-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <9.6.4-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <9.6.4-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <9.6.4-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <9.6.4-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <9.6.4-r0

## Details
PostgreSQL versions before 9.4.13, 9.5.8 and 9.6.4 are vulnerable to authorization flaw allowing remote authenticated attackers with no privileges on a large object to overwrite the entire contents of the object, resulting in a denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7548
