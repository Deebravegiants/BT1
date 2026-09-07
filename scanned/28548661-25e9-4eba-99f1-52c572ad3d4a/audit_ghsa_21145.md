# [H] Cross-site Scripting in Jenkins Rich Text Publisher Plugin

## Summary
Severity: High
Advisory: GHSA-2v6r-jf2g-j5q5
CVE: CVE-2022-34786
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-2v6r-jf2g-j5q5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:rich-text-publisher-plugin` — affected >=0

## Details
Jenkins Rich Text Publisher Plugin 1.4 and earlier does not escape the HTML message set by its post-build step, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to configure jobs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34786
- https://github.com/jenkinsci/rich-text-publisher-plugin
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-2332
