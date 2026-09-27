# [M] BIT-mariadb-2021-35604

## Summary
Severity: Medium
Advisory: BIT-mariadb-2021-35604
Aliases: BIT-mariadb-min-2021-35604, BIT-mysql-client-2021-35604, CVE-2021-35604
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2021-35604
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.6.0 <10.6.3

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: InnoDB). Supported versions that are affected are 5.7.35 and prior and 8.0.26 and prior. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server as well as unauthorized update, insert or delete access to some of MySQL Server accessible data. CVSS 3.1 Base Score 5.5 (Integrity and Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2UTW5KMPPDKIMGB4ULE2HS22HYLVKYIH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5MLAXYFLUDC636S46X34USCLDZAOFBM2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PRCU3RTIPVKPC3GMC76YW7DJEXUEY6FG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VGR5ZTB5QEDRRC6G5U6TFNCIVBBKGS5J/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XF3ZFPL3JJ26YRUGXLXQZYJBLZV3WC2C/
- https://security.netapp.com/advisory/ntap-20211022-0003/
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-35604
