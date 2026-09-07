# [H] Stored XSS vulnerability in Jenkins job build time trend

## Summary
Severity: High
Advisory: GHSA-qgj4-rc8m-44mq
CVE: CVE-2020-2220
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qgj4-rc8m-44mq
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.235.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.236 <2.245

## Details
Jenkins 2.244 and earlier, LTS 2.235.1 and earlier does not escape the agent name in the build time trend page, resulting in a stored cross-site scripting vulnerability.

Jenkins 2.245, LTS 2.235.2 escapes the agent name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2220
- https://github.com/jenkinsci/jenkins/commit/b43531acee280dedc3ea454a2fc5a1a42990ddda
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2020-07-15/#SECURITY-1868
- http://www.openwall.com/lists/oss-security/2020/07/15/5
