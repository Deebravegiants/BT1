# [M] ALPINE-CVE-2017-10268

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-10268
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-10-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-10268
Type: osv

## Affected
- Alpine:v3.4: `mariadb` — affected >=5.5.0 <10.1.32-r0
- Alpine:v3.5: `mariadb` — affected >=5.5.0 <10.1.32-r0
- Alpine:v3.6: `mariadb` — affected >=5.5.0 <10.1.32-r0
- Alpine:v3.7: `mariadb` — affected >=5.5.0 <10.1.32-r0

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Server: Replication). Supported versions that are affected are 5.5.57 and earlier, 5.6.37 and earlier and 5.7.19 and earlier. Difficult to exploit vulnerability allows high privileged attacker with logon to the infrastructure where MySQL Server executes to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized access to critical data or complete access to all MySQL Server accessible data. CVSS 3.0 Base Score 4.1 (Confidentiality impacts). CVSS Vector: (CVSS:3.0/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N).

## References
- https://security.alpinelinux.org/vuln/CVE-2017-10268
