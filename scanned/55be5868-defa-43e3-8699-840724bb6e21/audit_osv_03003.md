# [C] ALPINE-CVE-2024-23771

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-23771
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-23771
Type: osv

## Affected
- Alpine:v3.20: `darkhttpd` — affected >=0 <1.15-r0
- Alpine:v3.21: `darkhttpd` — affected >=0 <1.15-r0
- Alpine:v3.22: `darkhttpd` — affected >=0 <1.15-r0
- Alpine:v3.23: `darkhttpd` — affected >=0 <1.15-r0
- Alpine:v3.24: `darkhttpd` — affected >=0 <1.15-r0

## Details
darkhttpd before 1.15 uses strcmp (which is not constant time) to verify authentication, which makes it easier for remote attackers to bypass authentication via a timing side channel.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-23771
