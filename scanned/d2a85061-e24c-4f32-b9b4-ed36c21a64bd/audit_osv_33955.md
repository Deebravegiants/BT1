# [M] CVE-2025-53053

## Summary
Severity: Medium
Advisory: CVE-2025-53053
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-10-21
Source: https://osv.dev/vulnerability/CVE-2025-53053
Type: osv

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: Server: DML).  Supported versions that are affected are 8.0.0-8.0.43, 8.4.0-8.4.6 and  9.0.0-9.4.0. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server.  Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server as well as  unauthorized update, insert or delete access to some of MySQL Server accessible data. CVSS 3.1 Base Score 5.5 (Integrity and Availability impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53053.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-53053
- https://www.oracle.com/security-alerts/cpuoct2025.html
