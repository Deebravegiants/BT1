# [M] CVE-2025-30695

## Summary
Severity: Medium
Advisory: CVE-2025-30695
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-30695
Type: osv

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: InnoDB).  Supported versions that are affected are 8.0.0-8.0.41, 8.4.0-8.4.4 and  9.0.0-9.2.0. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server.  Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server as well as  unauthorized update, insert or delete access to some of MySQL Server accessible data. CVSS 3.1 Base Score 5.5 (Integrity and Availability impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30695.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-30695
- https://security.netapp.com/advisory/ntap-20250502-0006/
- https://www.oracle.com/security-alerts/cpuapr2025.html
