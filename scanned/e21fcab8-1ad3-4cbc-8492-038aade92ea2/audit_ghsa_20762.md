# [M] Jenkins Apprenda Plugin has Missing Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-52v4-wxrx-gjjm
CVE: CVE-2022-41251
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-52v4-wxrx-gjjm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:apprenda` — affected >=0

## Details
Jenkins Apprenda Plugin 2.2.0 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins. Those can be used as part of an attack to capture the credentials using another vulnerability.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41251
- https://github.com/jenkinsci/apprenda-plugin
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2710
- http://www.openwall.com/lists/oss-security/2022/09/21/5
