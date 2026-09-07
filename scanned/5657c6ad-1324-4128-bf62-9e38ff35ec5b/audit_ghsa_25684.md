# [H] Stored Cross-site Scripting vulnerability in Jenkins Gerrit Trigger Plugin

## Summary
Severity: High
Advisory: GHSA-455j-8hg5-8576
CVE: CVE-2022-29039
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-13
Source: https://github.com/advisories/GHSA-455j-8hg5-8576
Type: github-advisory

## Affected
- Maven: `com.sonyericsson.hudson.plugins.gerrit:gerrit-trigger` — affected >=0 <2.35.3

## Details
Jenkins Gerrit Trigger Plugin 2.35.2 and earlier does not escape the name and description of parameters on views displaying parameters, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

Exploitation of these vulnerabilities requires that parameters are listed on another page, like the \"Build With Parameters\" and \"Parameters\" pages provided by Jenkins (core), and that those pages are not hardened to prevent exploitation. Jenkins (core) has prevented exploitation of vulnerabilities of this kind on the \"Build With Parameters\" and \"Parameters\" pages since 2.44 and LTS 2.32.2 as part of the [SECURITY-353 / CVE-2017-2601](https://www.jenkins.io/security/advisory/2017-02-01/#persisted-cross-site-scripting-vulnerability-in-parameter-names-and-descriptions) fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29039
- https://github.com/jenkinsci/gerrit-trigger-plugin/commit/8b1d59645725e6f01057c1cf87170e321f99f6be
- https://github.com/jenkinsci/gerrit-trigger-plugin
- https://www.jenkins.io/security/advisory/2022-04-12/#SECURITY-2617
