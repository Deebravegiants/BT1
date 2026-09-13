# [M] Missing permission check in Jenkins Active Directory Plugin allows accessing domain health check page

## Summary
Severity: Medium
Advisory: GHSA-q6rq-4whr-r879
CVE: CVE-2020-2302
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q6rq-4whr-r879
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:active-directory` — affected >=0 <2.20

## Details
Jenkins Active Directory Plugin 2.19 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to access the domain health check diagnostic page.

Jenkins Active Directory Plugin 2.20 requires Overall/Administer permission to access the domain health check diagnostic page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2302
- https://github.com/jenkinsci/active-directory-plugin/commit/e6b5f2bf2f441bd679d35db1bd6f9576b148e3cb
- https://github.com/jenkinsci/active-directory-plugin
- https://www.jenkins.io/security/advisory/2020-11-04/#SECURITY-1999
