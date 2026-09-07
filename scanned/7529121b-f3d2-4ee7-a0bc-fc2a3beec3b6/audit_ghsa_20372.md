# [H] Cross-site Scripting in Jenkins Package Version Plugin

## Summary
Severity: High
Advisory: GHSA-gpw4-7mcw-m8vx
CVE: CVE-2022-34193
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-gpw4-7mcw-m8vx
Type: github-advisory

## Affected
- Maven: `org.lilicurroad.jenkins:packageversion` — affected >=0

## Details
Jenkins Package Version Plugin 1.0.1 and earlier does not escape the name of Package version parameters on views displaying parameters, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

Exploitation of this vulnerability requires that parameters are listed on another page, like the \"Build With Parameters\" and \"Parameters\" pages provided by Jenkins (core), and that those pages are not hardened to prevent exploitation. Jenkins (core) has prevented exploitation of vulnerabilities of this kind on the \"Build With Parameters\" and \"Parameters\" pages since 2.44 and LTS 2.32.2 as part of the [SECURITY-353 / CVE-2017-2601](https://www.jenkins.io/security/advisory/2017-02-01/#persisted-cross-site-scripting-vulnerability-in-parameter-names-and-descriptions) fix. Additionally, several plugins have previously been updated to list parameters in a way that prevents exploitation by default, see [SECURITY-2617 in the 2022-04-12 security advisory for a list](https://www.jenkins.io/security/advisory/2022-04-12/#SECURITY-2617).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34193
- https://github.com/jenkinsci/packageversion-plugin
- https://www.jenkins.io/security/advisory/2022-06-22/#SECURITY-2784
