# [H] ALPINE-CVE-2022-2625

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-2625
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-08-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-2625
Type: osv

## Affected
- Alpine:v3.13: `postgresql` — affected >=10.0 <13.8-r0
- Alpine:v3.14: `postgresql` — affected >=10.0 <13.8-r0
- Alpine:v3.15: `postgresql13` — affected >=0 <13.8-r0
- Alpine:v3.16: `postgresql13` — affected >=0 <13.8-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <14.5-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <14.5-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <14.5-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <14.5-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <14.5-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <14.5-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <14.5-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <14.5-r0

## Details
A vulnerability was found in PostgreSQL. This attack requires permission to create non-temporary objects in at least one schema, the ability to lure or wait for an administrator to create or update an affected extension in that schema, and the ability to lure or wait for a victim to use the object targeted in CREATE OR REPLACE or CREATE IF NOT EXISTS. Given all three prerequisites, this flaw allows an attacker to run arbitrary code as the victim role, which may be a superuser.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-2625
