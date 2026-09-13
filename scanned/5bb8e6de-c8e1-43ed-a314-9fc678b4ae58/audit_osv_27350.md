# [M] CVE-2024-20967

## Summary
Severity: Medium
Advisory: CVE-2024-20967
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2024-01-16
Source: https://osv.dev/vulnerability/CVE-2024-20967
Type: osv

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: Server: Replication).  Supported versions that are affected are 8.0.35 and prior and  8.2.0 and prior. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server.  Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server as well as  unauthorized update, insert or delete access to some of MySQL Server accessible data. CVSS 3.1 Base Score 5.5 (Integrity and Availability impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/20xxx/CVE-2024-20967.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-20967
- https://security.netapp.com/advisory/ntap-20240201-0003/
- https://www.oracle.com/security-alerts/cpujan2024.html
