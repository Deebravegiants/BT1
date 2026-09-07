# [M] Incorrect Permission Assignment for Critical Resource in Jenkins Credentials Binding Plugin

## Summary
Severity: Medium
Advisory: GHSA-gqm2-2gcx-p88w
CVE: CVE-2022-20616
CWE: CWE-732, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-01-13
Source: https://github.com/advisories/GHSA-gqm2-2gcx-p88w
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:credentials-binding` — affected >=1.25 <1.27.1
- Maven: `org.jenkins-ci.plugins:credentials-binding` — affected >=0 <1.24.1

## Details
Jenkins Credentials Binding Plugin prior to 1.27.1 and 1.24.1 does not perform a permission check in a method implementing form validation.

This allows attackers with Overall/Read access to validate if a credential ID refers to a secret file credential and whether it’s a zip file.

Credentials Binding Plugin 1.27.1 and 1.24.1 performs permission checks when validating secret file credentials IDs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-20616
- https://github.com/jenkinsci/credentials-binding-plugin/commit/2dd5eda721e52d9a5bf6748405adf965ba517d8a
- https://github.com/CVEProject/cvelist/blob/2d78eb36f4d084db7fb35f1535d8d84fdcb7d859/2022/20xxx/CVE-2022-20616.json
- https://github.com/jenkinsci/credentials-binding-plugin
- https://www.jenkins.io/security/advisory/2022-01-12/#SECURITY-2342
- http://www.openwall.com/lists/oss-security/2022/01/12/6
