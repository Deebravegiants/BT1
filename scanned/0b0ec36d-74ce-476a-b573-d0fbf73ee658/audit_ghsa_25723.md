# [M] Missing permission checks in AWS Credentials Plugin 

## Summary
Severity: Medium
Advisory: GHSA-m9gv-4523-jffm
CVE: CVE-2022-27199
CWE: CWE-276, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-03-16
Source: https://github.com/advisories/GHSA-m9gv-4523-jffm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:aws-credentials` — affected >=0 <191.vcb_f183ce58b_9

## Details
A missing permission check in Jenkins CloudBees AWS Credentials Plugin 189.v3551d5642995 and earlier allows attackers with Overall/Read permission to connect to an AWS service using an attacker-specified token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27199
- https://www.jenkins.io/security/advisory/2022-03-15/#SECURITY-2351
- http://www.openwall.com/lists/oss-security/2022/03/15/2
