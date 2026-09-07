# [H] Jenkins Stored Cross-site Scripting vulnerability 

## Summary
Severity: High
Advisory: GHSA-69vw-3pcm-84rw
CVE: CVE-2023-39151
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-26
Source: https://github.com/advisories/GHSA-69vw-3pcm-84rw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.402 <2.414.1
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.401.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.415 <2.416

## Details
Jenkins applies formatting to the console output of builds, transforming plain URLs into hyperlinks. Jenkins 2.415 and earlier, 2.414 and earlier, and LTS 2.401.2 and earlier does not sanitize or properly encode URLs of these hyperlinks in build logs. This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to control build log contents. Jenkins 2.416, 2.414.1, and LTS 2.401.3 encodes URLs of affected hyperlink annotations in build logs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39151
- https://github.com/jenkinsci/jenkins/commit/1b9f1ccdbb7d00705b036d1332908fe52c2cd7ae
- https://github.com/CVEProject/cvelist/blob/975222d6e43b5b1296dbc8a67d03704a1d2554e8/2023/39xxx/CVE-2023-39151.json
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2023-07-26/#SECURITY-3188
- http://www.openwall.com/lists/oss-security/2023/07/26/2
