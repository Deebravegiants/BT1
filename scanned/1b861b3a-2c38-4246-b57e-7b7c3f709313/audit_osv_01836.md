# [M] ALPINE-CVE-2020-1720

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-1720
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-03-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-1720
Type: osv

## Affected
- Alpine:v3.10: `postgresql` — affected >=9.6 <11.7-r0
- Alpine:v3.11: `postgresql` — affected >=9.6 <12.2-r0
- Alpine:v3.12: `postgresql` — affected >=9.6 <12.2-r0
- Alpine:v3.13: `postgresql` — affected >=9.6 <12.2-r0
- Alpine:v3.14: `postgresql` — affected >=9.6 <12.2-r0
- Alpine:v3.8: `postgresql` — affected >=9.6 <10.12-r0
- Alpine:v3.9: `postgresql` — affected >=9.6 <11.7-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <12.2-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <12.2-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <12.2-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <12.2-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <12.2-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <12.2-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <12.2-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <12.2-r0

## Details
A flaw was found in PostgreSQL's "ALTER ... DEPENDS ON EXTENSION", where sub-commands did not perform authorization checks. An authenticated attacker could use this flaw in certain configurations to perform drop objects such as function, triggers, et al., leading to database corruption. This issue affects PostgreSQL versions before 12.2, before 11.7, before 10.12 and before 9.6.17.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-1720
