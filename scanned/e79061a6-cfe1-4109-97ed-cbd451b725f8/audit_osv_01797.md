# [H] ALPINE-CVE-2020-15397

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-15397
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-15397
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
HylaFAX+ through 7.0.2 and HylaFAX Enterprise have scripts that execute binaries from directories writable by unprivileged users (e.g., locations under /var/spool/hylafax that are writable by the uucp account). This allows these users to execute code in the context of the user calling these binaries (often root).

## References
- https://security.alpinelinux.org/vuln/CVE-2020-15397
