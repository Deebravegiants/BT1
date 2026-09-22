# [M] ALPINE-CVE-2023-2455

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-2455
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2023-06-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-2455
Type: osv

## Affected
- Alpine:v3.13: `postgresql` — affected >=11.0 <13.11-r0
- Alpine:v3.14: `postgresql` — affected >=11.0 <13.11-r0
- Alpine:v3.15: `postgresql13` — affected >=0 <13.11-r0
- Alpine:v3.16: `postgresql13` — affected >=0 <13.11-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <14.8-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <14.8-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <14.8-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <14.8-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <15.3-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <15.3-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <15.3-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <15.3-r0

## Details
Row security policies disregard user ID changes after inlining; PostgreSQL could permit incorrect policies to be applied in certain cases where role-specific policies are used and a given query is planned under one role and then executed under other roles. This scenario can happen under security definer functions or when a common user and query is planned initially and then re-used across multiple SET ROLEs. Applying an incorrect policy may permit a user to complete otherwise-forbidden reads and modifications. This affects only databases that have used CREATE POLICY to define a row security policy.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-2455
