# [M] ALPINE-CVE-2017-3464

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-3464
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2017-04-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-3464
Type: osv

## Affected
- Alpine:v3.3: `mariadb` — affected >=5.5.0 <10.1.23-r0
- Alpine:v3.4: `mariadb` — affected >=5.5.0 <10.1.23-r0
- Alpine:v3.5: `mariadb` — affected >=5.5.0 <10.1.23-r0
- Alpine:v3.6: `mariadb` — affected >=5.5.0 <10.1.23-r0

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Server: DDL). Supported versions that are affected are 5.5.54 and earlier, 5.6.35 and earlier and 5.7.17 and earlier. Easily "exploitable" vulnerability allows low privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized update, insert or delete access to some of MySQL Server accessible data. CVSS 3.0 Base Score 4.3 (Integrity impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N).

## References
- https://security.alpinelinux.org/vuln/CVE-2017-3464
