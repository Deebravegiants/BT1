# [M] ALPINE-CVE-2018-11782

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-11782
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-11782
Type: osv

## Affected
- Alpine:v3.10: `subversion` — affected >=1.10.0 <1.12.2-r0
- Alpine:v3.11: `subversion` — affected >=1.10.0 <1.12.2-r0
- Alpine:v3.12: `subversion` — affected >=1.10.0 <1.12.2-r0
- Alpine:v3.13: `subversion` — affected >=1.10.0 <1.12.2-r0
- Alpine:v3.14: `subversion` — affected >=1.10.0 <1.12.2-r0
- Alpine:v3.15: `subversion` — affected >=1.10.0 <1.12.2-r0
- Alpine:v3.16: `subversion` — affected >=1.10.0 <1.12.2-r0
- Alpine:v3.17: `subversion` — affected >=1.10.0 <1.12.2-r0
- Alpine:v3.18: `subversion` — affected >=1.10.0 <1.12.2-r0
- Alpine:v3.19: `subversion` — affected >=1.10.0 <1.12.2-r0
- Alpine:v3.20: `subversion` — affected >=1.10.0 <1.12.2-r0
- Alpine:v3.21: `subversion` — affected >=1.10.0 <1.12.2-r0
- Alpine:v3.22: `subversion` — affected >=1.10.0 <1.12.2-r0
- Alpine:v3.23: `subversion` — affected >=1.10.0 <1.12.2-r0
- Alpine:v3.24: `subversion` — affected >=1.10.0 <1.12.2-r0
- Alpine:v3.7: `subversion` — affected >=1.10.0 <1.9.12-r0
- Alpine:v3.8: `subversion` — affected >=1.10.0 <1.10.6-r0
- Alpine:v3.9: `subversion` — affected >=1.10.0 <1.12.2-r0

## Details
In Apache Subversion versions up to and including 1.9.10, 1.10.4, 1.12.0, Subversion's svnserve server process may exit when a well-formed read-only request produces a particular answer. This can lead to disruption for users of the server.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-11782
