# [M] Stored Cross-site Scripting vulnerability in Jenkins Jira Plugin

## Summary
Severity: Medium
Advisory: GHSA-m3p3-2gp6-ghq8
CVE: CVE-2022-29041
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-13
Source: https://github.com/advisories/GHSA-m3p3-2gp6-ghq8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jira` — affected >=3.7.0 <3.7.1
- Maven: `org.jenkins-ci.plugins:jira` — affected >=0 <3.6.1

## Details
Jenkins Jira Plugin 3.7 and earlier, except 3.6.1, does not escape the name and description of Jira Issue and Jira Release Version parameters on views displaying parameters, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

Exploitation of this vulnerability requires that parameters are listed on another page, like the \"Build With Parameters\" and \"Parameters\" pages provided by Jenkins (core), and that those pages are not hardened to prevent exploitation. Jenkins (core) has prevented exploitation of vulnerabilities of this kind on the \"Build With Parameters\" and \"Parameters\" pages since 2.44 and LTS 2.32.2 as part of the [SECURITY-353 / CVE-2017-2601](https://www.jenkins.io/security/advisory/2017-02-01/#persisted-cross-site-scripting-vulnerability-in-parameter-names-and-descriptions) fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29041
- https://github.com/jenkinsci/jira-plugin/commit/e1eed0d64b4e32ce84946d632dab76c3f0ff6c4e
- https://github.com/jenkinsci/jira-plugin
- https://www.jenkins.io/security/advisory/2022-04-12/#SECURITY-2617
