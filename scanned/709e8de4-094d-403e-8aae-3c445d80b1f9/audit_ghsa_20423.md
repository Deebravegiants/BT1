# [M] Incorrect Permission Assignment for Critical Resource in Jenkins Bitbucket Branch Source Plugin

## Summary
Severity: Medium
Advisory: GHSA-w2mh-6xj5-f77f
CVE: CVE-2022-20618
CWE: CWE-732, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-01-13
Source: https://github.com/advisories/GHSA-w2mh-6xj5-f77f
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cloudbees-bitbucket-branch-source` — affected >=726.v7e6f53de133c <746.v350d2781c184
- Maven: `org.jenkins-ci.plugins:cloudbees-bitbucket-branch-source` — affected >=720.vbe985dd73d66 <725.vd9f8be0fa250
- Maven: `org.jenkins-ci.plugins:cloudbees-bitbucket-branch-source` — affected >=2.9.8 <2.9.11.2
- Maven: `org.jenkins-ci.plugins:cloudbees-bitbucket-branch-source` — affected >=0 <2.9.7.2

## Details
Jenkins Bitbucket Branch Source Plugin prior to 746.v350d2781c184, 725.vd9f8be0fa250, 2.9.11.2, and 2.9.7.2 does not perform permission checks in several HTTP endpoints.

This allows attackers with Overall/Read access to enumerate credentials IDs of credentials stored in Jenkins. Those can be used as part of an attack to capture the credentials using another vulnerability.

An enumeration of credentials IDs in Bitbucket Branch Source Plugin 746.v350d2781c184, 725.vd9f8be0fa250, 2.9.11.2, and 2.9.7.2 requires the appropriate permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-20618
- https://github.com/jenkinsci/bitbucket-branch-source-plugin/commit/467ed6c94af8735c4755d53145a54325ae82d073
- https://github.com/CVEProject/cvelist/blob/2d78eb36f4d084db7fb35f1535d8d84fdcb7d859/2022/20xxx/CVE-2022-20618.json
- https://github.com/jenkinsci/bitbucket-branch-source-plugin
- https://www.jenkins.io/security/advisory/2022-01-12/#SECURITY-2033
- http://www.openwall.com/lists/oss-security/2022/01/12/6
