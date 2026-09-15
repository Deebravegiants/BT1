# [M] ALPINE-CVE-2020-35176

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-35176
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-12-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-35176
Type: osv

## Affected
- Alpine:v3.10: `awstats` — affected >=0 <7.8-r0
- Alpine:v3.11: `awstats` — affected >=0 <7.8-r0
- Alpine:v3.12: `awstats` — affected >=0 <7.8-r1
- Alpine:v3.13: `awstats` — affected >=0 <7.8-r1
- Alpine:v3.14: `awstats` — affected >=0 <7.8-r1
- Alpine:v3.15: `awstats` — affected >=0 <7.8-r1
- Alpine:v3.16: `awstats` — affected >=0 <7.8-r1
- Alpine:v3.17: `awstats` — affected >=0 <7.8-r1
- Alpine:v3.18: `awstats` — affected >=0 <7.8-r1
- Alpine:v3.19: `awstats` — affected >=0 <7.8-r1
- Alpine:v3.20: `awstats` — affected >=0 <7.8-r1
- Alpine:v3.21: `awstats` — affected >=0 <7.8-r1
- Alpine:v3.22: `awstats` — affected >=0 <7.8-r1

## Details
In AWStats through 7.8, cgi-bin/awstats.pl?config= accepts a partial absolute pathname (omitting the initial /etc), even though it was intended to only read a file in the /etc/awstats/awstats.conf format. NOTE: this issue exists because of an incomplete fix for CVE-2017-1000501 and CVE-2020-29600.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-35176
