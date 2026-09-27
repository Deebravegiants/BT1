# [H] ALPINE-CVE-2017-12836

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-12836
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-12836
Type: osv

## Affected
- Alpine:v3.10: `cvs` — affected >=0 <1.12.12-r0
- Alpine:v3.11: `cvs` — affected >=0 <1.12.12-r0
- Alpine:v3.12: `cvs` — affected >=0 <1.12.12-r0
- Alpine:v3.13: `cvs` — affected >=0 <1.12.12-r0
- Alpine:v3.14: `cvs` — affected >=0 <1.12.12-r0
- Alpine:v3.15: `cvs` — affected >=0 <1.12.12-r0
- Alpine:v3.16: `cvs` — affected >=0 <1.12.12-r0
- Alpine:v3.17: `cvs` — affected >=0 <1.12.12-r0
- Alpine:v3.22: `cvs` — affected >=0 <1.12.12-r0
- Alpine:v3.23: `cvs` — affected >=0 <1.12.12-r0
- Alpine:v3.24: `cvs` — affected >=0 <1.12.12-r0
- Alpine:v3.8: `cvs` — affected >=0 <1.12.12-r0
- Alpine:v3.9: `cvs` — affected >=0 <1.12.12-r0

## Details
CVS 1.12.x, when configured to use SSH for remote repositories, might allow remote attackers to execute arbitrary code via a repository URL with a crafted hostname, as demonstrated by "-oProxyCommand=id;localhost:/bar."

## References
- https://security.alpinelinux.org/vuln/CVE-2017-12836
