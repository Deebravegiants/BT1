# [M] Stored XSS vulnerability in Jenkins button labels

## Summary
Severity: Medium
Advisory: GHSA-wv63-gwr9-5c55
CVE: CVE-2021-21608
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-wv63-gwr9-5c55
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.275
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.263.2 <2.275

## Details
Jenkins 2.274 and earlier, LTS 2.263.1 and earlier does not escape button labels in the Jenkins UI.

This results in a cross-site scripting vulnerability exploitable by attackers with the ability to control button labels. An example of buttons with a user-controlled label are the buttons of the Pipeline `input` step.

Jenkins 2.275, LTS 2.263.2 escapes button labels in the Jenkins UI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21608
- https://github.com/jenkinsci/jenkins/commit/8c451b08886561a914ef0c30cbb9d40ea33a9bbe
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2021-01-13/#SECURITY-2035
