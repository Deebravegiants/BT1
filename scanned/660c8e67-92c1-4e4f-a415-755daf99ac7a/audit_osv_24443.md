# [M] CVE-2023-21869

## Summary
Severity: Medium
Advisory: CVE-2023-21869
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2023-01-17
Source: https://osv.dev/vulnerability/CVE-2023-21869
Type: osv

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: InnoDB).  Supported versions that are affected are 8.0.31 and prior. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server.  Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server as well as  unauthorized update, insert or delete access to some of MySQL Server accessible data. CVSS 3.1 Base Score 5.5 (Integrity and Availability impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/21xxx/CVE-2023-21869.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-21869
- https://www.oracle.com/security-alerts/cpujan2023.html
