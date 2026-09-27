# [H] CVE-2026-46863

## Summary
Severity: High
Advisory: CVE-2026-46863
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/CVE-2026-46863
Type: osv

## Details
Vulnerability in the MySQL Server, MySQL Cluster product of Oracle MySQL (component: Server: Connection Handling).  Supported versions that are affected are MySQL Server: 8.4.0-8.4.9, 9.0.0-9.7.0; MySQL Cluster: 8.0.11-8.0.46, 8.4.0-8.4.9 and  9.0.0-9.7.0. Easily exploitable vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise MySQL Server, MySQL Cluster.  Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server, MySQL Cluster. CVSS 3.1 Base Score 7.5 (Availability impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46863.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46863
- https://www.oracle.com/security-alerts/cspujun2026.html
