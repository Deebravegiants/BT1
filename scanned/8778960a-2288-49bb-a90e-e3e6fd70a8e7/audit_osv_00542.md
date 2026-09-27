# [H] ALPINE-CVE-2017-15365

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-15365
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-15365
Type: osv

## Affected
- Alpine:v3.4: `mariadb` — affected >=10.2.0 <10.1.32-r0
- Alpine:v3.5: `mariadb` — affected >=10.2.0 <10.1.32-r0
- Alpine:v3.6: `mariadb` — affected >=10.2.0 <10.1.32-r0
- Alpine:v3.7: `mariadb` — affected >=10.2.0 <10.1.32-r0

## Details
sql/event_data_objects.cc in MariaDB before 10.1.30 and 10.2.x before 10.2.10 and Percona XtraDB Cluster before 5.6.37-26.21-3 and 5.7.x before 5.7.19-29.22-3 allows remote authenticated users with SQL access to bypass intended access restrictions and replicate data definition language (DDL) statements to cluster nodes by leveraging incorrect ordering of DDL replication and ACL checking.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-15365
