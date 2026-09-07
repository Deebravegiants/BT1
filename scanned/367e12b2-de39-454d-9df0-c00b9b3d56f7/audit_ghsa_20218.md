# [M] Observable timing discrepancy allows determining username validity in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-9grj-j43m-mjqr
CVE: CVE-2022-34174
CWE: CWE-203, CWE-208
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-9grj-j43m-mjqr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.334 <2.356
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.332.4

## Details
In Jenkins 2.355 and earlier, LTS 2.332.3 and earlier, an observable timing discrepancy on the login form allows distinguishing between login attempts with an invalid username, and login attempts with a valid username and wrong password, when using the Jenkins user database security realm. This allows attackers to determine the validity of attacker-specified usernames.

Login attempts with an invalid username now validate a synthetic password to eliminate the timing discrepancy in Jenkins 2.356, LTS 2.332.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34174
- https://github.com/jenkinsci/jenkins/commit/957ef5902f2e40b6358e6d10f12b26f9dbd2f75a
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2022-06-22/#SECURITY-2566
