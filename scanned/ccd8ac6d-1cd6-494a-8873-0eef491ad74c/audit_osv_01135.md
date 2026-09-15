# [H] ALPINE-CVE-2018-20683

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-20683
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-20683
Type: osv

## Affected
- Alpine:v3.10: `gitolite` — affected >=0 <3.6.11-r0
- Alpine:v3.11: `gitolite` — affected >=0 <3.6.11-r0
- Alpine:v3.12: `gitolite` — affected >=0 <3.6.11-r0
- Alpine:v3.13: `gitolite` — affected >=0 <3.6.11-r0
- Alpine:v3.14: `gitolite` — affected >=0 <3.6.11-r0
- Alpine:v3.15: `gitolite` — affected >=0 <3.6.11-r0
- Alpine:v3.16: `gitolite` — affected >=0 <3.6.11-r0
- Alpine:v3.17: `gitolite` — affected >=0 <3.6.11-r0
- Alpine:v3.18: `gitolite` — affected >=0 <3.6.11-r0
- Alpine:v3.19: `gitolite` — affected >=0 <3.6.11-r0
- Alpine:v3.20: `gitolite` — affected >=0 <3.6.11-r0
- Alpine:v3.21: `gitolite` — affected >=0 <3.6.11-r0
- Alpine:v3.22: `gitolite` — affected >=0 <3.6.11-r0
- Alpine:v3.23: `gitolite` — affected >=0 <3.6.11-r0
- Alpine:v3.24: `gitolite` — affected >=0 <3.6.11-r0
- Alpine:v3.6: `gitolite` — affected >=0 <3.6.11-r0
- Alpine:v3.7: `gitolite` — affected >=0 <3.6.11-r0
- Alpine:v3.8: `gitolite` — affected >=0 <3.6.11-r0
- Alpine:v3.9: `gitolite` — affected >=0 <3.6.11-r0

## Details
commands/rsync in Gitolite before 3.6.11, if .gitolite.rc enables rsync, mishandles the rsync command line, which allows attackers to have a "bad" impact by triggering use of an option other than -v, -n, -q, or -P.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-20683
