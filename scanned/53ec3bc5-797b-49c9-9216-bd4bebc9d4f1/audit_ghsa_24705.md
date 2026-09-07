# [H] Jenkins Cross-site Scripting vulnerability in project naming strategy

## Summary
Severity: High
Advisory: GHSA-9g4m-ffx6-c29g
CVE: CVE-2020-2230
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9g4m-ffx6-c29g
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.235.4
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.236 <2.252

## Details
Jenkins 2.251 and earlier, LTS 2.235.3 and earlier does not escape the project naming strategy description, that is displayed on item creation.\n\nThis results in a stored cross-site scripting (XSS) vulnerability exploitable by users with Overall/Manage permission.\n\nJenkins 2.252, LTS 2.235.4 escapes the project naming strategy description.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2230
- https://github.com/jenkinsci/jenkins/commit/e49f690939596acbc9a1be64128b2c7eaf91a6db
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2020-08-12/#SECURITY-1957
- http://packetstormsecurity.com/files/160443/Jenkins-2.235.3-Cross-Site-Scripting.html
- http://www.openwall.com/lists/oss-security/2020/08/12/4
