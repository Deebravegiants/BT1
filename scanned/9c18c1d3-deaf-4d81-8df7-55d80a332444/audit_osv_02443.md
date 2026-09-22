# [H] ALPINE-CVE-2022-24052

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-24052
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-24052
Type: osv

## Affected
- Alpine:v3.12: `mariadb` — affected >=10.2.0 <10.4.24-r0
- Alpine:v3.13: `mariadb` — affected >=10.2.0 <10.5.15-r0
- Alpine:v3.14: `mariadb` — affected >=10.2.0 <10.5.15-r0
- Alpine:v3.15: `mariadb` — affected >=10.2.0 <10.6.7-r0
- Alpine:v3.16: `mariadb` — affected >=10.2.0 <10.6.7-r0
- Alpine:v3.17: `mariadb` — affected >=10.2.0 <10.6.7-r0
- Alpine:v3.18: `mariadb` — affected >=10.2.0 <10.6.7-r0
- Alpine:v3.19: `mariadb` — affected >=10.2.0 <10.6.7-r0
- Alpine:v3.20: `mariadb` — affected >=10.2.0 <10.6.7-r0
- Alpine:v3.21: `mariadb` — affected >=10.2.0 <10.6.7-r0
- Alpine:v3.22: `mariadb` — affected >=10.2.0 <10.6.7-r0
- Alpine:v3.23: `mariadb` — affected >=10.2.0 <10.6.7-r0
- Alpine:v3.24: `mariadb` — affected >=10.2.0 <10.6.7-r0

## Details
MariaDB CONNECT Storage Engine Heap-based Buffer Overflow Privilege Escalation Vulnerability. This vulnerability allows local attackers to escalate privileges on affected installations of MariaDB. Authentication is required to exploit this vulnerability. The specific flaw exists within the processing of SQL queries. The issue results from the lack of proper validation of the length of user-supplied data prior to copying it to a fixed-length heap-based buffer. An attacker can leverage this vulnerability to escalate privileges and execute arbitrary code in the context of the service account. Was ZDI-CAN-16190.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-24052
