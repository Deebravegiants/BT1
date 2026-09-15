# [M] CVE-2022-21539

## Summary
Severity: Medium
Advisory: CVE-2022-21539
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-07-19
Source: https://osv.dev/vulnerability/CVE-2022-21539
Type: osv

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: InnoDB). Supported versions that are affected are 8.0.29 and prior. Difficult to exploit vulnerability allows low privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized update, insert or delete access to some of MySQL Server accessible data as well as unauthorized read access to a subset of MySQL Server accessible data and unauthorized ability to cause a partial denial of service (partial DOS) of MySQL Server. CVSS 3.1 Base Score 5.0 (Confidentiality, Integrity and Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L).

## References
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21539.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-21539
- https://security.netapp.com/advisory/ntap-20220729-0004/
