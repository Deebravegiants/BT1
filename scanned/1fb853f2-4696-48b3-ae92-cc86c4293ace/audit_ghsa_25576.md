# [M] Stored Cross-site Scripting in Jenkins Mask Passwords Plugin

## Summary
Severity: Medium
Advisory: GHSA-pjm3-f4vh-3h3h
CVE: CVE-2022-29043
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-13
Source: https://github.com/advisories/GHSA-pjm3-f4vh-3h3h
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:mask-passwords` — affected >=0 <3.1

## Details
Jenkins Mask Passwords Plugin 3.0 and earlier does not escape the name and description of Non-Stored Password parameters on views displaying parameters, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

Exploitation of this vulnerability requires that parameters are listed on another page, like the \"Build With Parameters\" and \"Parameters\" pages provided by Jenkins (core), and that those pages are not hardened to prevent exploitation. Jenkins (core) has prevented exploitation of vulnerabilities of this kind on the \"Build With Parameters\" and \"Parameters\" pages since 2.44 and LTS 2.32.2 as part of the [SECURITY-353 / CVE-2017-2601](https://www.jenkins.io/security/advisory/2017-02-01/#persisted-cross-site-scripting-vulnerability-in-parameter-names-and-descriptions) fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29043
- https://github.com/jenkinsci/mask-passwords-plugin/commit/55022b3f1935dc005c4075161c176b29bce7b849
- https://github.com/jenkinsci/mask-passwords-plugin
- https://www.jenkins.io/security/advisory/2022-04-12/#SECURITY-2617
