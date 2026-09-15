# [M] CVE-2022-21489

## Summary
Severity: Medium
Advisory: CVE-2022-21489
CVSS: 6.3 (CVSS:3.1/AV:A/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-04-19
Source: https://osv.dev/vulnerability/CVE-2022-21489
Type: osv

## Details
Vulnerability in the MySQL Cluster product of Oracle MySQL (component: Cluster: General). Supported versions that are affected are 7.4.35 and prior, 7.5.25 and prior, 7.6.21 and prior and 8.0.28 and prior. Difficult to exploit vulnerability allows high privileged attacker with access to the physical communication segment attached to the hardware where the MySQL Cluster executes to compromise MySQL Cluster. Successful attacks require human interaction from a person other than the attacker. Successful attacks of this vulnerability can result in takeover of MySQL Cluster. CVSS 3.1 Base Score 6.3 (Confidentiality, Integrity and Availability impacts). CVSS Vector: (CVSS:3.1/AV:A/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:H).

## References
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21489.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-21489
- https://security.netapp.com/advisory/ntap-20220429-0005/
