# [M] CVE-2022-21352

## Summary
Severity: Medium
Advisory: CVE-2022-21352
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2022-01-19
Source: https://osv.dev/vulnerability/CVE-2022-21352
Type: osv

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: InnoDB). Supported versions that are affected are 8.0.26 and prior. Difficult to exploit vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized creation, deletion or modification access to critical data or all MySQL Server accessible data and unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.1 Base Score 5.9 (Integrity and Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:H/A:H).

## References
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21352.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-21352
- https://security.netapp.com/advisory/ntap-20220121-0008/
