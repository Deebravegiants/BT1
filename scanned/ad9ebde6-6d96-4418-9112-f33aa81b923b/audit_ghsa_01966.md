# [M] Cross-Site Request Forgery in Jenkins Credentials Plugin

## Summary
Severity: Medium
Advisory: GHSA-gchq-9r68-6jwv
CVE: CVE-2021-21648
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-16
Source: https://github.com/advisories/GHSA-gchq-9r68-6jwv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:credentials` — affected >=2.3.16 <2.3.19
- Maven: `org.jenkins-ci.plugins:credentials` — affected >=2.3.15 <2.3.15.1
- Maven: `org.jenkins-ci.plugins:credentials` — affected >=2.3.14 <2.3.14.1
- Maven: `org.jenkins-ci.plugins:credentials` — affected >=2.3.8 <2.3.13.1
- Maven: `org.jenkins-ci.plugins:credentials` — affected >=2.3.1 <2.3.7.1
- Maven: `org.jenkins-ci.plugins:credentials` — affected >=0 <2.3.0.1

## Details
Jenkins Credentials Plugin prior to 2.3.19, 2.3.15.1, 2.3.14.1, 2.3.13.1, 2.3.7.1, and 2.3.0.1 does not escape user-controlled information on a view it provides, resulting in a reflected cross-site scripting (XSS) vulnerability.

Jenkins Credentials Plugin 2.3.19, 2.3.15.1, 2.3.14.1, 2.3.13.1, 2.3.7.1, and 2.3.0.1 restricts the user-controlled information it provides to a safe subset.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21648
- https://github.com/jenkinsci/credentials-plugin/commit/41f3ec1143f80a7e80ab9a4a5f861f26fd3792cc
- https://github.com/CVEProject/cvelist/blob/2d78eb36f4d084db7fb35f1535d8d84fdcb7d859/2021/21xxx/CVE-2021-21648.json
- https://github.com/jenkinsci/credentials-plugin
- https://www.jenkins.io/security/advisory/2021-05-11/#SECURITY-2349
