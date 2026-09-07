# [H] Jenkins Cross-Site Scripting vulnerability in help icons

## Summary
Severity: High
Advisory: GHSA-hvmc-7g2x-r3p9
CVE: CVE-2020-2229
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hvmc-7g2x-r3p9
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.235.4
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.236 <2.252

## Details
Jenkins 2.251 and earlier, LTS 2.235.3 and earlier does not escape the tooltip content of help icons. Tooltip values can be contributed by plugins, some of which use user-specified values.
This results in a stored cross-site scripting (XSS) vulnerability.
Jenkins 2.252, LTS 2.235.4 escapes the tooltip content of help icons.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2229
- https://github.com/jenkinsci/jenkins/commit/fe4cbe03804d6240d0b58d0b2301ea9530a34916
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2020-08-12/#SECURITY-1955
- http://packetstormsecurity.com/files/160443/Jenkins-2.235.3-Cross-Site-Scripting.html
- http://www.openwall.com/lists/oss-security/2020/08/12/4
