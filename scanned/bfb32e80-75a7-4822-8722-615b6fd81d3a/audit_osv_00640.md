# [M] ALPINE-CVE-2017-3636

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-3636
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2017-08-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-3636
Type: osv

## Affected
- Alpine:v3.3: `mariadb` — affected >=5.5.0 <10.1.26-r0
- Alpine:v3.4: `mariadb` — affected >=5.5.0 <10.1.26-r0
- Alpine:v3.5: `mariadb` — affected >=5.5.0 <10.1.26-r0
- Alpine:v3.6: `mariadb` — affected >=5.5.0 <10.1.26-r0

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Client programs). Supported versions that are affected are 5.5.56 and earlier and 5.6.36 and earlier. Easily exploitable vulnerability allows low privileged attacker with logon to the infrastructure where MySQL Server executes to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized update, insert or delete access to some of MySQL Server accessible data as well as unauthorized read access to a subset of MySQL Server accessible data and unauthorized ability to cause a partial denial of service (partial DOS) of MySQL Server. CVSS 3.0 Base Score 5.3 (Confidentiality, Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L).

## References
- https://security.alpinelinux.org/vuln/CVE-2017-3636
