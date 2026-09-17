# [H] ALPINE-CVE-2018-1053

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-1053
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1053
Type: osv

## Affected
- Alpine:v3.10: `postgresql` — affected >=9.3.0 <10.2-r0
- Alpine:v3.11: `postgresql` — affected >=9.3.0 <10.2-r0
- Alpine:v3.12: `postgresql` — affected >=9.3.0 <10.2-r0
- Alpine:v3.13: `postgresql` — affected >=9.3.0 <10.2-r0
- Alpine:v3.14: `postgresql` — affected >=9.3.0 <10.2-r0
- Alpine:v3.4: `postgresql` — affected >=9.3.0 <9.5.11-r0
- Alpine:v3.5: `postgresql` — affected >=9.3.0 <9.6.7-r0
- Alpine:v3.6: `postgresql` — affected >=9.3.0 <9.6.7-r0
- Alpine:v3.7: `postgresql` — affected >=9.3.0 <10.2-r0
- Alpine:v3.8: `postgresql` — affected >=9.3.0 <10.2-r0
- Alpine:v3.9: `postgresql` — affected >=9.3.0 <10.2-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <10.2-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <10.2-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <10.2-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <10.2-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <10.2-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <10.2-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <10.2-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <10.2-r0

## Details
In postgresql 9.3.x before 9.3.21, 9.4.x before 9.4.16, 9.5.x before 9.5.11, 9.6.x before 9.6.7 and 10.x before 10.2, pg_upgrade creates file in current working directory containing the output of `pg_dumpall -g` under umask which was in effect when the user invoked pg_upgrade, and not under 0077 which is normally used for other temporary files. This can allow an authenticated attacker to read or modify the one file, which may contain encrypted or unencrypted database passwords. The attack is infeasible if a directory mode blocks the attacker searching the current working directory or if the prevailing umask blocks the attacker opening the file.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1053
