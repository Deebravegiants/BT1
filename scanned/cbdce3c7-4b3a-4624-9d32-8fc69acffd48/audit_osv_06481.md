# [M] BIT-mariadb-2021-2372

## Summary
Severity: Medium
Advisory: BIT-mariadb-2021-2372
Aliases: BIT-mariadb-min-2021-2372, BIT-mysql-client-2021-2372, CVE-2021-2372
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2021-2372
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.6.0 <10.6.4

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: InnoDB). Supported versions that are affected are 5.7.34 and prior and 8.0.25 and prior. Difficult to exploit vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.1 Base Score 4.4 (Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2UTW5KMPPDKIMGB4ULE2HS22HYLVKYIH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6OO2Q5PIFURXLLKCIJE6XF6VL4LLMNO5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OPJAGVMRKODR4QIXQSVEM4BLRZUM7P3R/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VGR5ZTB5QEDRRC6G5U6TFNCIVBBKGS5J/
- https://security.netapp.com/advisory/ntap-20210723-0001/
- https://www.oracle.com/security-alerts/cpujul2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-2372
