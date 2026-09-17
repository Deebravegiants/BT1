# [H] ALPINE-CVE-2020-15396

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-15396
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-15396
Type: osv

## Affected
- Alpine:v3.10: `hylafaxplus` — affected >=0 <7.0.0-r4
- Alpine:v3.11: `hylafaxplus` — affected >=0 <7.0.1-r2
- Alpine:v3.12: `hylafaxplus` — affected >=0 <7.0.2-r2
- Alpine:v3.13: `hylafaxplus` — affected >=0 <7.0.2-r2
- Alpine:v3.14: `hylafaxplus` — affected >=0 <7.0.2-r2
- Alpine:v3.15: `hylafaxplus` — affected >=0 <7.0.2-r2
- Alpine:v3.16: `hylafaxplus` — affected >=0 <7.0.2-r2
- Alpine:v3.17: `hylafaxplus` — affected >=0 <7.0.2-r2
- Alpine:v3.18: `hylafaxplus` — affected >=0 <7.0.2-r2
- Alpine:v3.19: `hylafaxplus` — affected >=0 <7.0.2-r2
- Alpine:v3.20: `hylafaxplus` — affected >=0 <7.0.2-r2
- Alpine:v3.9: `hylafaxplus` — affected >=0 <7.0.0-r1

## Details
In HylaFAX+ through 7.0.2 and HylaFAX Enterprise, the faxsetup utility calls chown on files in user-owned directories. By winning a race, a local attacker could use this to escalate his privileges to root.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-15396
