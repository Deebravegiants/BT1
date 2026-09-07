# [H] Cross-Site Request Forgery in Jenkins Bitbucket Branch Source Plugin

## Summary
Severity: High
Advisory: GHSA-w4jv-6rg4-pr4m
CVE: CVE-2022-20619
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-01-13
Source: https://github.com/advisories/GHSA-w4jv-6rg4-pr4m
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cloudbees-bitbucket-branch-source` — affected >=726.v7e6f53de133c <746.v350d2781c184
- Maven: `org.jenkins-ci.plugins:cloudbees-bitbucket-branch-source` — affected >=720.vbe985dd73d66 <725.vd9f8be0fa250
- Maven: `org.jenkins-ci.plugins:cloudbees-bitbucket-branch-source` — affected >=2.9.8 <2.9.11.2
- Maven: `org.jenkins-ci.plugins:cloudbees-bitbucket-branch-source` — affected >=0 <2.9.7.2

## Details
Jenkins Bitbucket Branch Source Plugin prior to 746.v350d2781c184, 725.vd9f8be0fa250, 2.9.11.2, and 2.9.7.2 does not require POST requests for an HTTP endpoint, resulting in a cross-site request forgery (CSRF) vulnerability.

This allows attackers with Overall/Read access to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

Bitbucket Branch Source Plugin 746.v350d2781c184, 725.vd9f8be0fa250, 2.9.11.2, and 2.9.7.2 requires POST requests for the affected HTTP endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-20619
- https://github.com/jenkinsci/bitbucket-branch-source-plugin/commit/a596f651a4b3bfe31a087c4d392e81c0167ab551
- https://github.com/CVEProject/cvelist/blob/2d78eb36f4d084db7fb35f1535d8d84fdcb7d859/2022/20xxx/CVE-2022-20619.json
- https://github.com/jenkinsci/bitbucket-branch-source-plugin
- https://www.jenkins.io/security/advisory/2022-01-12/#SECURITY-2467
- http://www.openwall.com/lists/oss-security/2022/01/12/6
