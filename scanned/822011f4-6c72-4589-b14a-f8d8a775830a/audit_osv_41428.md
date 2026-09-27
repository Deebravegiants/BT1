# [M] CVE-2026-60188

## Summary
Severity: Medium
Advisory: CVE-2026-60188
CVSS: 4.4 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-60188
Type: osv

## Details
Vulnerability in the MySQL Server, MySQL Cluster product of Oracle MySQL (component: Server: Replication).  Supported versions that are affected are MySQL Server: 8.4.0-8.4.10, 9.7.0-9.7.1; MySQL Cluster: 8.0.0-8.0.47, 8.4.0-8.4.10 and  9.7.0-9.7.1. Difficult to exploit vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server, MySQL Cluster.  Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server, MySQL Cluster. CVSS 3.1 Base Score 4.4 (Availability impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/60xxx/CVE-2026-60188.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-60188
- https://www.oracle.com/security-alerts/cpujul2026.html
