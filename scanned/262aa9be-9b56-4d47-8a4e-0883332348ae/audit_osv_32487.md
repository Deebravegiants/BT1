# [M] CVE-2025-30721

## Summary
Severity: Medium
Advisory: CVE-2025-30721
CVSS: 4.0 (CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-30721
Type: osv

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: Server: UDF).  Supported versions that are affected are 8.0.0-8.0.41, 8.4.0-8.4.4 and  9.0.0-9.2.0. Difficult to exploit vulnerability allows high privileged attacker with logon to the infrastructure where MySQL Server executes to compromise MySQL Server.  Successful attacks require human interaction from a person other than the attacker. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.1 Base Score 4.0 (Availability impacts).  CVSS Vector: (CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:N/I:N/A:H).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30721.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-30721
- https://security.netapp.com/advisory/ntap-20250502-0006/
- https://www.oracle.com/security-alerts/cpuapr2025.html
