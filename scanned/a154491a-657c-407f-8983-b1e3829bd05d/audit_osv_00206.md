# [H] ALPINE-CVE-2016-6664

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-6664
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-6664
Type: osv

## Affected
- Alpine:v3.10: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.11: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.12: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.13: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.14: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.15: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.16: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.17: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.18: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.19: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.20: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.21: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.22: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.23: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.24: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.3: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.4: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.5: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.6: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.7: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.8: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.9: `mariadb` — affected >=5.5.0 <10.1.21-r0

## Details
mysqld_safe in Oracle MySQL through 5.5.51, 5.6.x through 5.6.32, and 5.7.x through 5.7.14; MariaDB; Percona Server before 5.5.51-38.2, 5.6.x before 5.6.32-78-1, and 5.7.x before 5.7.14-8; and Percona XtraDB Cluster before 5.5.41-37.0, 5.6.x before 5.6.32-25.17, and 5.7.x before 5.7.14-26.17, when using file-based logging, allows local users with access to the mysql account to gain root privileges via a symlink attack on error logs and possibly other files.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-6664
