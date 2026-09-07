# [M] Cross-Site Request Forgery in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-p92q-7fhh-mq35
CVE: CVE-2022-20612
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-p92q-7fhh-mq35
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.320 <2.330
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.319.2

## Details
Jenkins 2.329 and earlier, LTS 2.319.1 and earlier does not require POST requests for the HTTP endpoint handling manual build requests when no security realm is set, resulting in a cross-site request forgery (CSRF) vulnerability.

This vulnerability allows attackers to trigger build of job without parameters.

Jenkins 2.330, LTS 2.319.2 requires POST requests for the affected HTTP endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-20612
- https://github.com/jenkinsci/jenkins/commit/b5c3764681f3b4ce83d0e78f6a9327925640d57e
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/changelog-stable/#v2.319.2
- https://www.jenkins.io/changelog/#v2.330
- https://www.jenkins.io/security/advisory/2022-01-12/#SECURITY-2558
- https://www.oracle.com/security-alerts/cpuapr2022.html
- http://www.openwall.com/lists/oss-security/2022/01/12/6
