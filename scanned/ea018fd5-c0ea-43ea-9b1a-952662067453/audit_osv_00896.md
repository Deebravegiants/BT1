# [H] ALPINE-CVE-2018-1061

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-1061
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1061
Type: osv

## Affected
- Alpine:v3.10: `python2` — affected >=0 <2.7.15-r0
- Alpine:v3.11: `python2` — affected >=0 <2.7.15-r0
- Alpine:v3.12: `python2` — affected >=0 <2.7.15-r0
- Alpine:v3.5: `python2` — affected >=0 <2.7.15-r0
- Alpine:v3.6: `python2` — affected >=0 <2.7.15-r0
- Alpine:v3.7: `python2` — affected >=0 <2.7.15-r0
- Alpine:v3.9: `python2` — affected >=0 <2.7.15-r0
- Alpine:v3.5: `python3` — affected >=0 <3.5.6-r0
- Alpine:v3.6: `python3` — affected >=0 <3.6.5-r0
- Alpine:v3.7: `python3` — affected >=0 <3.6.5-r0
- Alpine:v3.8: `python3` — affected >=0 <3.6.6-r0

## Details
python before versions 2.7.15, 3.4.9, 3.5.6rc1, 3.6.5rc1 and 3.7.0 is vulnerable to catastrophic backtracking in the difflib.IS_LINE_JUNK method.  An attacker could use this flaw to cause denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1061
