# [H] Race Condition in Jenkins

## Summary
Severity: High
Advisory: GHSA-r5x3-2446-hrp7
CVE: CVE-2017-1000503
CWE: CWE-362
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-r5x3-2446-hrp7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.81 <2.89.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.90 <2.95

## Details
A race condition during Jenkins 2.81 through 2.94 (inclusive); 2.89.1 startup could result in the wrong order of execution of commands during initialization. This could in rare cases result in failure to initialize the setup wizard on the first startup. This resulted in multiple security-related settings not being set to their usual strict default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000503
- https://github.com/jenkinsci/jenkins/commit/ccc374a7176d7704941fb494589790b7673efe2
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2017-12-14
