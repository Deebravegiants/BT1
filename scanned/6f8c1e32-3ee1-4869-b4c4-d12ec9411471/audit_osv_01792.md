# [C] ALPINE-CVE-2020-15180

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2020-15180
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-15180
Type: osv

## Affected
- Alpine:v3.10: `mariadb` — affected >=10.1.0 <10.3.25-r0
- Alpine:v3.11: `mariadb` — affected >=10.1.0 <10.4.15-r0
- Alpine:v3.12: `mariadb` — affected >=10.1.0 <10.4.15-r0
- Alpine:v3.13: `mariadb` — affected >=10.1.0 <10.5.6-r0
- Alpine:v3.14: `mariadb` — affected >=10.1.0 <10.5.6-r0
- Alpine:v3.15: `mariadb` — affected >=10.1.0 <10.5.6-r0
- Alpine:v3.16: `mariadb` — affected >=10.1.0 <10.5.6-r0
- Alpine:v3.17: `mariadb` — affected >=10.1.0 <10.5.6-r0
- Alpine:v3.18: `mariadb` — affected >=10.1.0 <10.5.6-r0
- Alpine:v3.19: `mariadb` — affected >=10.1.0 <10.5.6-r0
- Alpine:v3.20: `mariadb` — affected >=10.1.0 <10.5.6-r0
- Alpine:v3.21: `mariadb` — affected >=10.1.0 <10.5.6-r0
- Alpine:v3.22: `mariadb` — affected >=10.1.0 <10.5.6-r0
- Alpine:v3.23: `mariadb` — affected >=10.1.0 <10.5.6-r0
- Alpine:v3.24: `mariadb` — affected >=10.1.0 <10.5.6-r0
- Alpine:v3.9: `mariadb` — affected >=10.1.0 <10.3.25-r0

## Details
A flaw was found in the mysql-wsrep component of mariadb. Lack of input sanitization in `wsrep_sst_method` allows for command injection that can be exploited by a remote attacker to execute arbitrary commands on galera cluster nodes. This threatens the system's confidentiality, integrity, and availability. This flaw affects mariadb versions before 10.1.47, before 10.2.34, before 10.3.25, before 10.4.15 and before 10.5.6.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-15180
