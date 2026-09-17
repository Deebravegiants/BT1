# [C] ALPINE-CVE-2017-1000501

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-1000501
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-1000501
Type: osv

## Affected
- Alpine:v3.10: `awstats` — affected >=0 <7.6-r2
- Alpine:v3.11: `awstats` — affected >=0 <7.6-r2
- Alpine:v3.12: `awstats` — affected >=0 <7.6-r2
- Alpine:v3.13: `awstats` — affected >=0 <7.6-r2
- Alpine:v3.14: `awstats` — affected >=0 <7.6-r2
- Alpine:v3.15: `awstats` — affected >=0 <7.6-r2
- Alpine:v3.16: `awstats` — affected >=0 <7.6-r2
- Alpine:v3.17: `awstats` — affected >=0 <7.6-r2
- Alpine:v3.18: `awstats` — affected >=0 <7.6-r2
- Alpine:v3.19: `awstats` — affected >=0 <7.6-r2
- Alpine:v3.20: `awstats` — affected >=0 <7.6-r2
- Alpine:v3.21: `awstats` — affected >=0 <7.6-r2
- Alpine:v3.22: `awstats` — affected >=0 <7.6-r2
- Alpine:v3.4: `awstats` — affected >=0 <7.5-r2
- Alpine:v3.5: `awstats` — affected >=0 <7.5-r2
- Alpine:v3.6: `awstats` — affected >=0 <7.6-r1
- Alpine:v3.7: `awstats` — affected >=0 <7.6-r2
- Alpine:v3.8: `awstats` — affected >=0 <7.6-r2
- Alpine:v3.9: `awstats` — affected >=0 <7.6-r2

## Details
Awstats version 7.6 and earlier is vulnerable to a path traversal flaw in the handling of the "config" and "migrate" parameters resulting in unauthenticated remote code execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-1000501
