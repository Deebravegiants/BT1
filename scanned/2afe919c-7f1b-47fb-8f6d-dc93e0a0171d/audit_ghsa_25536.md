# [M] Stored Cross-site Scripting vulnerability in Jenkins Job Generator Plugin

## Summary
Severity: Medium
Advisory: GHSA-f3jq-9c79-j65m
CVE: CVE-2022-29042
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-13
Source: https://github.com/advisories/GHSA-f3jq-9c79-j65m
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jobgenerator` — affected >=0

## Details
Jenkins Job Generator Plugin 1.22 and earlier does not escape the name and description of Generator Parameter and Generator Choice parameters on Job Generator jobs' Build With Parameters views, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

Exploitation of this vulnerability requires that parameters are listed on another page, like the \"Build With Parameters\" and \"Parameters\" pages provided by Jenkins (core), and that those pages are not hardened to prevent exploitation. Jenkins (core) has prevented exploitation of vulnerabilities of this kind on the \"Build With Parameters\" and \"Parameters\" pages since 2.44 and LTS 2.32.2 as part of the [SECURITY-353 / CVE-2017-2601](https://www.jenkins.io/security/advisory/2017-02-01/#persisted-cross-site-scripting-vulnerability-in-parameter-names-and-descriptions) fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29042
- https://github.com/jenkinsci/jobgenerator-plugin
- https://www.jenkins.io/security/advisory/2022-04-12/#SECURITY-2617
