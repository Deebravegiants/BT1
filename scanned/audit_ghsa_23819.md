# [M] Missing permission check in Jenkins Oracle Cloud Infrastructure Compute Classic Plugin 

## Summary
Severity: Medium
Advisory: GHSA-74c2-965q-mqjw
CVE: CVE-2019-10457
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-74c2-965q-mqjw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:oracle-cloud-infrastructure-compute-classic` — affected >=0

## Details
A missing permission check in Jenkins Oracle Cloud Infrastructure Compute Classic Plugin allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10457
- https://jenkins.io/security/advisory/2019-10-16/#SECURITY-1462
- http://www.openwall.com/lists/oss-security/2019/10/16/6
