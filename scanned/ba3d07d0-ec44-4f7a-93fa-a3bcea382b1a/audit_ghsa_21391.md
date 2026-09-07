# [H] Stored XSS vulnerability in Jenkins Custom Checkbox Parameter Plugin

## Summary
Severity: High
Advisory: GHSA-vf5v-6wjm-vr7v
CVE: CVE-2022-43425
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-vf5v-6wjm-vr7v
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:custom-checkbox-parameter` — affected >=0

## Details
Custom Checkbox Parameter Plugin 1.4 and earlier does not escape the name and description of the parameter types it provides.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

Exploitation of this vulnerability requires that parameters are listed on another page, like the \"Build With Parameters\" and \"Parameters\" pages provided by Jenkins (core), and that those pages are not hardened to prevent exploitation. Jenkins (core) has prevented exploitation of vulnerabilities of this kind on the \"Build With Parameters\" and \"Parameters\" pages since 2.44 and LTS 2.32.2 as part of the [SECURITY-353 / CVE-2017-2601](https://www.jenkins.io/security/advisory/2017-02-01/#persisted-cross-site-scripting-vulnerability-in-parameter-names-and-descriptions) fix. Additionally, several plugins have previously been updated to list parameters in a way that prevents exploitation by default, see [SECURITY-2617 in the 2022-04-12 security advisory for a list](https://www.jenkins.io/security/advisory/2022-04-12/#SECURITY-2617).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43425
- https://github.com/jenkinsci/custom-checkbox-parameter-plugin
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2797
- http://www.openwall.com/lists/oss-security/2022/10/19/3
