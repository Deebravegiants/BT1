# [M] Stored XSS vulnerability in Jenkins on new item page

## Summary
Severity: Medium
Advisory: GHSA-mj7q-cmf3-mg7h
CVE: CVE-2021-21611
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mj7q-cmf3-mg7h
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.263.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.264 <2.275

## Details
Jenkins 2.274 and earlier, LTS 2.263.1 and earlier does not escape display names and IDs of item types shown on the New Item page.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to specify display names or IDs of item types.

As of the publication of this advisory, the Jenkins security team is not aware of any plugins published via the Jenkins project update center that allow doing this.
Jenkins 2.275, LTS 2.263.2 escapes display names and IDs of item types shown on the New Item page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21611
- https://github.com/jenkinsci/jenkins/commit/8c451b08886561a914ef0c30cbb9d40ea33a9bbe
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2021-01-13/#SECURITY-2171
