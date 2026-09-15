# [M] BIT-mariadb-2021-2032

## Summary
Severity: Medium
Advisory: BIT-mariadb-2021-2032
Aliases: BIT-mariadb-min-2021-2032, BIT-mysql-client-2021-2032, CVE-2021-2032
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2021-2032
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.0.0 <10.0.11

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: Information Schema). Supported versions that are affected are 5.7.32 and prior and 8.0.22 and prior. Easily exploitable vulnerability allows low privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized read access to a subset of MySQL Server accessible data. CVSS 3.1 Base Score 4.3 (Confidentiality impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N).

## References
- https://security.gentoo.org/glsa/202105-27
- https://security.netapp.com/advisory/ntap-20210219-0003/
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-2032
