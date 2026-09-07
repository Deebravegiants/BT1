# [M] Jenkins RapidDeploy Plugin missing permission check

## Summary
Severity: Medium
Advisory: GHSA-m4vq-v7hw-7fqq
CVE: CVE-2019-16571
CWE: CWE-285, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m4vq-v7hw-7fqq
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:rapiddeploy-jenkins` — affected >=0

## Details
A missing permission check in Jenkins RapidDeploy Plugin 4.1 and earlier allows attackers with Overall/Read permission to connect to an attacker-specified web server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16571
- https://jenkins.io/security/advisory/2019-12-17/#SECURITY-1604
- http://www.openwall.com/lists/oss-security/2019/12/17/1
