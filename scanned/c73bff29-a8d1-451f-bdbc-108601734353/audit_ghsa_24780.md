# [H] Stored XSS vulnerability in Jenkins 'keep forever' badge icon

## Summary
Severity: High
Advisory: GHSA-864v-5q2g-fr64
CVE: CVE-2020-2222
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-864v-5q2g-fr64
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.235.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.236 <2.245

## Details
Jenkins 2.244 and earlier, LTS 2.235.1 and earlier does not escape the job name in the 'Keep this build forever' badge tooltip. This results in a stored cross-site scripting (XSS) vulnerability exploitable by users able to configure job names.

As job names do not generally support the character set needed for XSS, this is believed to be difficult to exploit in common configurations.

Jenkins 2.245, LTS 2.235.2 escapes the job name in the 'Keep this build forever' badge tooltip.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2222
- https://github.com/jenkinsci/jenkins/commit/e7443ef2ef255253231f3f1db0034fae39f0cba5
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2020-07-15/#SECURITY-1902
- http://www.openwall.com/lists/oss-security/2020/07/15/5
