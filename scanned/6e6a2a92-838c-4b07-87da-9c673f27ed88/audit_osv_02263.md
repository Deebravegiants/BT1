# [M] ALPINE-CVE-2021-3677

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-3677
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-03-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3677
Type: osv

## Affected
- Alpine:v3.11: `postgresql` — affected >=11.0 <12.8-r0
- Alpine:v3.12: `postgresql` — affected >=11.0 <12.8-r0
- Alpine:v3.13: `postgresql` — affected >=11.0 <13.4-r0
- Alpine:v3.14: `postgresql` — affected >=11.0 <13.4-r0
- Alpine:v3.15: `postgresql13` — affected >=0 <13.4-r0
- Alpine:v3.16: `postgresql13` — affected >=0 <13.4-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <13.4-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <13.4-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <13.4-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <13.4-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <13.4-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <13.4-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <13.4-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <13.4-r0

## Details
A flaw was found in postgresql. A purpose-crafted query can read arbitrary bytes of server memory. In the default configuration, any authenticated database user can complete this attack at will. The attack does not require the ability to create objects. If server settings include max_worker_processes=0, the known versions of this attack are infeasible. However, undiscovered variants of the attack may be independent of that setting.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3677
