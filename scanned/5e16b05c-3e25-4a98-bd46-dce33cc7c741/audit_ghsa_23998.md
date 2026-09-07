# [H] Missing permission check in Jenkins Pipeline Maven Integration Plugin allow capturing credentials

## Summary
Severity: High
Advisory: GHSA-mrr8-fcg7-p2wg
CVE: CVE-2020-2234
CWE: CWE-285, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mrr8-fcg7-p2wg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:pipeline-maven` — affected >=0 <3.8.3

## Details
Pipeline Maven Integration Plugin 3.8.2 and earlier does not perform a permission check in a method implementing form validation.

This allows users with Overall/Read access to Jenkins to connect to an attacker-specified JDBC URL using attacker-specified credentials IDs obtained through another method, potentially capturing credentials stored in Jenkins.

Additionally, this form validation method does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

Pipeline Maven Integration Plugin 3.8.3 requires POST requests and Job/Configure permission for the affected form validation method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2234
- https://github.com/jenkinsci/pipeline-maven-plugin
- https://jenkins.io/security/advisory/2020-08-12/#SECURITY-1794%20(2)
- http://www.openwall.com/lists/oss-security/2020/08/12/4
