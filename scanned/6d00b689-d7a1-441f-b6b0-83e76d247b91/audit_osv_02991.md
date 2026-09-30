# [M] ALPINE-CVE-2024-21096

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-21096
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-21096
Type: osv

## Affected
- Alpine:v3.18: `mariadb` — affected >=0 <10.11.8-r0
- Alpine:v3.19: `mariadb` — affected >=0 <10.11.11-r0
- Alpine:v3.20: `mariadb` — affected >=0 <10.11.8-r0
- Alpine:v3.21: `mariadb` — affected >=0 <10.11.8-r0
- Alpine:v3.22: `mariadb` — affected >=0 <10.11.8-r0
- Alpine:v3.23: `mariadb` — affected >=0 <10.11.8-r0
- Alpine:v3.24: `mariadb` — affected >=0 <10.11.8-r0

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: Client: mysqldump).  Supported versions that are affected are 8.0.36 and prior and  8.3.0 and prior. Difficult to exploit vulnerability allows unauthenticated attacker with logon to the infrastructure where MySQL Server executes to compromise MySQL Server.  Successful attacks of this vulnerability can result in  unauthorized update, insert or delete access to some of MySQL Server accessible data as well as  unauthorized read access to a subset of MySQL Server accessible data and unauthorized ability to cause a partial denial of service (partial DOS) of MySQL Server. CVSS 3.1 Base Score 4.9 (Confidentiality, Integrity and Availability impacts).  CVSS Vector: (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L).

## References
- https://security.alpinelinux.org/vuln/CVE-2024-21096
