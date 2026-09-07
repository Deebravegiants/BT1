# [H] Cross site scripting in Jenkins Selection tasks Plugin

## Summary
Severity: High
Advisory: GHSA-mw4r-5mfc-m5vc
CVE: CVE-2022-30967
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-18
Source: https://github.com/advisories/GHSA-mw4r-5mfc-m5vc
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:selection-tasks-plugin` — affected >=0

## Details
Jenkins Selection tasks Plugin 1.0 and earlier does not escape the name and description of Script Selection task variable parameters on views displaying parameters. This results in stored cross-site scripting (XSS) vulnerabilities exploitable by attackers with Item/Configure permission.

Exploitation of this vulnerability requires that parameters are listed on another page, like the \"Build With Parameters\" and \"Parameters\" pages provided by Jenkins (core), and that those pages are not hardened to prevent exploitation. Jenkins (core) has prevented exploitation of vulnerabilities of this kind on the \"Build With Parameters\" and \"Parameters\" pages since 2.44 and LTS 2.32.2 as part of the [SECURITY-353 / CVE-2017-2601](https://www.jenkins.io/security/advisory/2017-02-01/#persisted-cross-site-scripting-vulnerability-in-parameter-names-and-descriptions) fix. Additionally, several plugins have previously been updated to list parameters in a way that prevents exploitation by default, see [SECURITY-2617 in the 2022-04-12 security advisory for a list](https://www.jenkins.io/security/advisory/2022-04-12/#SECURITY-2617).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30967
- https://github.com/jenkinsci/selection-tasks-plugin
- https://www.jenkins.io/security/advisory/2022-05-17/#SECURITY-2717
