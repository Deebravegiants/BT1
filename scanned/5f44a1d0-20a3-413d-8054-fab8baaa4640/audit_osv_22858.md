# [M] CVE-2022-39402

## Summary
Severity: Medium
Advisory: CVE-2022-39402
CVSS: 4.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2022-10-18
Source: https://osv.dev/vulnerability/CVE-2022-39402
Type: osv

## Details
Vulnerability in the MySQL Shell product of Oracle MySQL (component: Shell: Core Client). Supported versions that are affected are 8.0.30 and prior. Easily exploitable vulnerability allows unauthenticated attacker with logon to the infrastructure where MySQL Shell executes to compromise MySQL Shell. While the vulnerability is in MySQL Shell, attacks may significantly impact additional products (scope change). Successful attacks of this vulnerability can result in unauthorized read access to a subset of MySQL Shell accessible data. CVSS 3.1 Base Score 4.3 (Confidentiality impacts). CVSS Vector: (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N).

## References
- https://www.oracle.com/security-alerts/cpuoct2022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39402.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-39402
