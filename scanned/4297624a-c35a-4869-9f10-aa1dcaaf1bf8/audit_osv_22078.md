# [M] CVE-2022-21527

## Summary
Severity: Medium
Advisory: CVE-2022-21527
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2022-07-19
Source: https://osv.dev/vulnerability/CVE-2022-21527
Type: osv

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: Server: Optimizer). Supported versions that are affected are 8.0.29 and prior. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server as well as unauthorized update, insert or delete access to some of MySQL Server accessible data. CVSS 3.1 Base Score 5.5 (Integrity and Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H).

## References
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21527.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZI4Q7XW5QLUTOACRHBIEYZ6SZB6TIEMT/
- https://nvd.nist.gov/vuln/detail/CVE-2022-21527
- https://security.netapp.com/advisory/ntap-20220729-0004/
