# [H] ALPINE-CVE-2022-1552

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-1552
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-1552
Type: osv

## Affected
- Alpine:v3.13: `postgresql` — affected >=10.0 <13.7-r0
- Alpine:v3.14: `postgresql` — affected >=10.0 <13.7-r0
- Alpine:v3.15: `postgresql13` — affected >=0 <13.7-r0
- Alpine:v3.16: `postgresql13` — affected >=0 <13.7-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <14.3-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <14.3-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <14.3-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <14.3-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <14.3-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <14.3-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <14.3-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <14.3-r0

## Details
A flaw was found in PostgreSQL. There is an issue with incomplete efforts to operate safely when a privileged user is maintaining another user's objects. The Autovacuum, REINDEX, CREATE INDEX, REFRESH MATERIALIZED VIEW, CLUSTER, and pg_amcheck commands activated relevant protections too late or not at all during the process. This flaw allows an attacker with permission to create non-temporary objects in at least one schema to execute arbitrary SQL functions under a superuser identity.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-1552
